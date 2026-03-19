"""
Cluster Intelligence Service — AI-powered exam topic clustering.

Analyzes exam questions and suggests optimal topic clusters using AI
with multi-perspective review (student, instructor, examiner).
"""
import json
import logging
from typing import Dict, List, Any, Optional

from app.infrastructure.persistence.repositories.exams.questions import (
    ExamQuestionRepository,
)
from app.infrastructure.persistence.repositories.exams.topic_clusters import (
    ExamTopicClusterRepository,
)

logger = logging.getLogger(__name__)


class ClusterIntelligenceService:
    """Generate AI-powered cluster suggestions for exam types."""

    @staticmethod
    def suggest_clusters(
        exam_type_key: str,
        region: str = 'alle',
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Analyze questions and suggest optimal clusters.

        Gathers all available context (questions, points, topics,
        existing clusters) and asks AI to propose clusters with
        multi-perspective validation.

        Returns structured suggestion with clusters, reasoning,
        and warnings.
        """
        options = options or {}

        context = _build_analysis_context(exam_type_key, region)
        if not context['questions']:
            logger.warning(
                "No questions for cluster suggestion: type=%s region=%s",
                exam_type_key, region,
            )
            return {
                'status': 'no_data',
                'message': f'No questions found for {exam_type_key}',
                'clusters': [],
                'warnings': [
                    'No exam questions available for analysis',
                ],
            }

        prompt = _build_cluster_prompt(context)

        from app.infrastructure.ai.adapter import AIAdapter
        from app.infrastructure.ai.task_model_resolver import resolve_model_for_task
        provider = options.get('provider')
        model = options.get('model')
        if not provider or not model:
            resolved_provider, resolved_model = resolve_model_for_task('taxonomy')
            provider = provider or resolved_provider
            model = model or resolved_model
        adapter = AIAdapter(provider=provider, model=model)

        logger.info(
            "Requesting cluster suggestion for %s: "
            "%d questions, %d topics, %.0f total points",
            exam_type_key,
            context['question_count'],
            len(context['topic_distribution']),
            context['total_points'],
        )

        response = adapter.chat([
            {'role': 'system', 'content': _SYSTEM_PROMPT},
            {'role': 'user', 'content': prompt},
        ], response_format='json')

        suggestion = _parse_suggestion(response, context)
        suggestion['exam_type_key'] = exam_type_key
        suggestion['region'] = region
        suggestion['analysis_context'] = {
            'question_count': context['question_count'],
            'topic_count': len(context['topic_distribution']),
            'total_points': context['total_points'],
        }

        logger.info(
            "Cluster suggestion for %s: %d clusters, %d warnings",
            exam_type_key,
            len(suggestion.get('clusters', [])),
            len(suggestion.get('warnings', [])),
        )

        return suggestion

    @staticmethod
    def apply_suggestion(
        exam_type_key: str,
        clusters: List[Dict],
    ) -> int:
        """Apply approved cluster suggestion to DB.

        Admin reviews AI suggestion, optionally modifies, then
        confirms. This persists the approved clusters.
        """
        return ExamTopicClusterRepository.replace_all_clusters(
            exam_type_key, clusters,
        )


_SYSTEM_PROMPT = """\
You are an exam analysis expert specializing in German IHK \
(Industrie- und Handelskammer) vocational exams.

Your task: Analyze exam question data and suggest optimal topic \
clusters for exam preparation courses.

You MUST respond with valid JSON matching this schema:
{
  "clusters": [
    {
      "cluster_key": "lowercase_snake_case",
      "label": {"de": "German name", "en": "English name"},
      "topics": ["topic1", "topic2"],
      "reasoning": "Why these topics belong together",
      "point_share_pct": 15.5,
      "question_count": 42
    }
  ],
  "reviews": {
    "student_perspective": "From exam taker view...",
    "instructor_perspective": "From teacher view...",
    "examiner_perspective": "From IHK examiner view..."
  },
  "warnings": ["List of gaps or concerns"],
  "overall_assessment": "Brief summary of cluster quality"
}

Guidelines:
- Aim for 5-10 clusters (too few = too broad, too many = fragmented)
- Each cluster should have at least 3 questions
- Clusters should match how the exam is actually structured
- Consider point distribution: heavy topics deserve their own cluster
- Map ALL topics to a cluster (no orphans)
- Use the actual topic_key values from the data (not invented keys)
- Labels must be in German and English
- Flag any gaps where exam catalog topics have few/no questions
- Consider difficulty distribution within clusters"""


def _build_analysis_context(
    exam_type_key: str, region: str,
) -> Dict[str, Any]:
    """Gather all context needed for cluster analysis."""
    questions = ExamQuestionRepository.find_for_course_generation(
        exam_type_key, region,
    )

    topic_counts: Dict[str, Dict] = {}
    for q in questions:
        for topic in (q.get('topics') or []):
            if topic not in topic_counts:
                topic_counts[topic] = {
                    'count': 0,
                    'points': 0.0,
                    'sample_texts': [],
                }
            topic_counts[topic]['count'] += 1
            topic_counts[topic]['points'] += float(
                q.get('points', 0),
            )
            if len(topic_counts[topic]['sample_texts']) < 2:
                text = q.get('question_text', '')[:200]
                if text:
                    topic_counts[topic]['sample_texts'].append(text)

    total_points = sum(
        float(q.get('points', 0)) for q in questions
    )

    existing = ExamTopicClusterRepository.find_by_exam_type(
        exam_type_key,
    )

    return {
        'exam_type_key': exam_type_key,
        'questions': questions,
        'question_count': len(questions),
        'topic_distribution': topic_counts,
        'total_points': total_points,
        'existing_clusters': existing,
    }


def _build_cluster_prompt(context: Dict[str, Any]) -> str:
    """Build the user prompt with all analysis data."""
    topic_lines = []
    for topic, data in sorted(
        context['topic_distribution'].items(),
        key=lambda x: x[1]['points'],
        reverse=True,
    ):
        pct = (
            data['points'] / context['total_points'] * 100
            if context['total_points'] > 0 else 0
        )
        sample = ''
        if data['sample_texts']:
            sample = data['sample_texts'][0][:100]
        topic_lines.append(
            f"  {topic}: {data['count']} questions, "
            f"{data['points']:.0f} points ({pct:.1f}%)"
            f"{' — e.g. ' + sample if sample else ''}"
        )

    existing_info = ''
    if context['existing_clusters']:
        existing_info = "\n\nExisting clusters (for reference):\n"
        for c in context['existing_clusters']:
            label = c.get('label', {}).get('de', '?')
            topic_count = len(c.get('topics', []))
            existing_info += (
                f"  {c['cluster_key']}: {label} "
                f"— {topic_count} topics\n"
            )

    return (
        f"Analyze this exam data and suggest optimal topic clusters.\n\n"
        f"Exam Type: {context['exam_type_key']}\n"
        f"Total Questions: {context['question_count']}\n"
        f"Total Points: {context['total_points']:.0f}\n\n"
        f"Topic Distribution (sorted by points):\n"
        f"{chr(10).join(topic_lines)}"
        f"{existing_info}\n\n"
        f"Please suggest clusters and review from three perspectives:\n"
        f"1. STUDENT: Can I prepare for the full exam with these?\n"
        f"2. INSTRUCTOR: Is the didactic structure sound?\n"
        f"3. EXAMINER: Does this cover all exam areas proportionally?"
    )


def _parse_suggestion(
    response: Dict[str, Any],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """Parse and validate the AI response."""
    try:
        content = response.get('content', '')
        if isinstance(content, str):
            data = json.loads(content)
        else:
            data = content
    except (json.JSONDecodeError, TypeError):
        logger.exception("Failed to parse cluster suggestion response")
        return {
            'status': 'parse_error',
            'clusters': [],
            'warnings': [
                'AI response could not be parsed as JSON',
            ],
            'raw_response': str(
                response.get('content', ''),
            )[:500],
        }

    clusters = data.get('clusters', [])
    warnings = list(data.get('warnings', []))

    # Validate: check all DB topics are covered
    all_topics = set(context['topic_distribution'].keys())
    covered_topics = set()
    for c in clusters:
        covered_topics.update(c.get('topics', []))

    orphaned = all_topics - covered_topics
    if orphaned:
        warnings.append(
            f"Uncovered topics ({len(orphaned)}): "
            f"{', '.join(sorted(orphaned))}"
        )

    return {
        'status': 'success',
        'clusters': clusters,
        'reviews': data.get('reviews', {}),
        'warnings': warnings,
        'overall_assessment': data.get('overall_assessment', ''),
    }
