<!--
  Calculation Modal - IHK-Prüfungsstil Kalkulation

  Features:
  - Strukturierte Kalkulationstabelle (wie bei IHK)
  - Verschiedene Kalkulationsarten (Bezugs-, Verkaufs-, Handelskalkulation)
  - Schritt-für-Schritt Eingabe mit Teilpunkten
  - Automatische Berechnung bei korrekten Eingaben
  - Folgefehler-Erkennung
  - Dark Mode Support
-->

<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-content">
        <!-- Header -->
        <div class="modal-header">
          <div class="flex items-center gap-3">
            <span class="text-2xl">🧮</span>
            <div>
              <h2 class="modal-title">
                {{ getCalculationTitle() }}
              </h2>
              <p class="modal-subtitle">
                {{ methodName || 'LM12 - Mathe Interaktiv' }}
              </p>
            </div>
          </div>
          <button @click="$emit('close')" class="close-btn">✕</button>
        </div>

        <!-- Body -->
        <div class="modal-body">
          <!-- Main Menu: Type Selector -->
          <div v-if="currentMode === 'menu'" class="type-selector">
            <h3 class="selector-title">Wähle die Kalkulationsarten:</h3>
            <p class="selector-hint">Wähle eine oder mehrere Arten zum Üben</p>

            <div class="type-grid">
              <button
                v-for="type in calculationTypes"
                :key="type.id"
                @click="toggleCalculationType(type.id)"
                class="type-card"
                :class="{ active: selectedTypes.includes(type.id) }"
              >
                <span class="type-check">{{ selectedTypes.includes(type.id) ? '✓' : '' }}</span>
                <span class="type-icon">{{ type.icon }}</span>
                <span class="type-name">{{ type.name }}</span>
                <span class="type-desc">{{ type.description }}</span>
                <span class="type-count">{{ type.taskCount }} Aufgaben</span>
              </button>
            </div>

            <!-- Quick Select Buttons -->
            <div class="quick-select">
              <button @click="selectAllTypes" class="quick-btn">
                🔀 Alle mischen
              </button>
              <button @click="clearSelection" class="quick-btn" :disabled="selectedTypes.length === 0">
                ✕ Auswahl löschen
              </button>
            </div>

            <!-- Selection Summary -->
            <div v-if="selectedTypes.length > 0" class="selection-summary">
              <span class="summary-text">
                {{ selectedTypes.length === 1 ? getTypeName(selectedTypes[0]) : `${selectedTypes.length} Arten gemischt` }}
              </span>
              <span class="summary-count">{{ totalSelectedTasks }} Aufgaben verfügbar</span>
            </div>

            <div class="mode-buttons">
              <button
                @click="startGuidedTutorial"
                class="btn-tutorial"
                :disabled="selectedTypes.length === 0"
              >
                📖 Theorie & Taschenrechner-Anleitung
              </button>
              <button
                @click="showPracticeSelect"
                class="btn-start"
                :disabled="selectedTypes.length === 0"
              >
                🎯 Direkt üben
              </button>
            </div>
          </div>

          <!-- Practice Mode Selection -->
          <div v-else-if="currentMode === 'practice-select'" class="practice-select">
            <button @click="backToMenu" class="back-link">← Zurück</button>
            <h3 class="selector-title">Wie möchtest du üben?</h3>
            <p class="selector-subtitle">{{ getCalculationTitle() }}</p>

            <div class="difficulty-grid">
              <button @click="startPracticeNormal" class="difficulty-card easy">
                <span class="difficulty-icon">📝</span>
                <span class="difficulty-name">Mit Bezeichnungen</span>
                <span class="difficulty-desc">Die Schritte (LEP, ZEP, BEP...) werden angezeigt</span>
                <span class="difficulty-badge">Einstieg</span>
              </button>

              <button @click="startPracticeExam" class="difficulty-card hard">
                <span class="difficulty-icon">✏️</span>
                <span class="difficulty-name">Prüfungsmodus</span>
                <span class="difficulty-desc">Nur leere Felder - alles selbst ausfüllen wie in der IHK-Prüfung</span>
                <span class="difficulty-badge">Prüfungsnah</span>
              </button>
            </div>
          </div>

          <!-- Guided Mode: Tutor explains a real task -->
          <div v-else-if="currentMode === 'guided'" class="guided-area">
            <!-- Tutor Avatar (prominent) -->
            <div class="guided-tutor-section">
              <TutorAvatar
                :visible="tutorVisible"
                :text="tutorText"
                :auto-play="tutorAutoPlay"
                :voice="tutorVoice"
                :mood="tutorMood"
                position="inline"
                :show-name="true"
                tutor-name="Lumi"
                @speech-end="onTutorSpeechEnd"
              />
            </div>

            <!-- Progress -->
            <div class="guided-progress">
              <div class="progress-bar-bg">
                <div
                  class="progress-bar-fill"
                  :style="{ width: `${((guidedStep + 1) / guidedSteps.length) * 100}%` }"
                ></div>
              </div>
              <span class="progress-text">{{ guidedStep + 1 }} / {{ guidedSteps.length }}</span>
            </div>

            <!-- Current Step Card -->
            <div v-if="currentGuidedStep" class="guided-card">
              <div class="guided-card-header">
                <span class="step-badge">Schritt {{ guidedStep + 1 }}</span>
                <h3>{{ currentGuidedStep.title }}</h3>
              </div>

              <!-- Show the calculation schema with current values highlighted -->
              <div class="guided-schema">
                <table class="calc-schema-preview">
                  <tbody>
                    <tr
                      v-for="(step, idx) in calculationSteps"
                      :key="idx"
                      :class="{ 'highlighted': currentGuidedStep.highlight === `step-${idx}` }"
                    >
                      <td class="schema-step">{{ idx + 1 }}</td>
                      <td class="schema-name">{{ step.name }}</td>
                      <td class="schema-operator">{{ step.operator === 'minus' ? '−' : '+' }}</td>
                      <td class="schema-value">{{ formatCurrency(step.correctValue) }}</td>
                    </tr>
                    <tr class="result-row">
                      <td class="schema-step">{{ calculationSteps.length + 1 }}</td>
                      <td class="schema-name"><strong>{{ getResultLabel() }}</strong></td>
                      <td class="schema-operator">=</td>
                      <td class="schema-value"><strong>{{ formatCurrency(currentTask.result) }}</strong></td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Calculator hint if available -->
              <div v-if="currentGuidedStep.calculator" class="calculator-hint">
                <span class="calc-icon">🔢</span>
                <span class="calc-label">Taschenrechner:</span>
                <code class="calc-input">{{ currentGuidedStep.calculator }}</code>
              </div>
            </div>

            <!-- Navigation -->
            <div class="guided-nav">
              <button
                @click="prevGuidedStep"
                class="nav-btn nav-btn-back"
                :disabled="guidedStep === 0"
              >
                ← Zurück
              </button>

              <button
                v-if="guidedStep < guidedSteps.length - 1"
                @click="nextGuidedStep"
                class="nav-btn nav-btn-next"
              >
                Weiter →
              </button>
              <button
                v-else
                @click="finishGuidedTutorial"
                class="nav-btn nav-btn-start"
              >
                Jetzt selbst üben! 🚀
              </button>
            </div>

            <button @click="backToMenu" class="skip-link">
              ← Zurück zum Menü
            </button>
          </div>

          <!-- Tutorial Mode (ADHS-friendly) -->
          <div v-else-if="currentMode === 'tutorial'" class="tutorial-area">
            <!-- Tutor Avatar -->
            <TutorAvatar
              ref="avatarRef"
              :visible="tutorVisible"
              :text="tutorText"
              :auto-play="tutorAutoPlay"
              :voice="tutorVoice"
              :mood="tutorMood"
              position="inline"
              :show-name="true"
              tutor-name="Lumi"
              @speech-end="onTutorSpeechEnd"
              @skip="onTutorSkip"
            />

            <!-- Progress Bar -->
            <div class="progress-section">
              <div class="progress-bar-bg">
                <div
                  class="progress-bar-fill"
                  :style="{ width: `${((tutorialStep + 1) / tutorialSteps.length) * 100}%` }"
                ></div>
              </div>
              <div class="progress-text">
                {{ tutorialStep + 1 }} / {{ tutorialSteps.length }}
              </div>
            </div>

            <!-- Main Card (one thing at a time) -->
            <div class="tutorial-card" v-if="currentTutorialStep" :key="tutorialStep">
              <!-- Card Header -->
              <div class="card-header">
                <span class="card-step">Schritt {{ tutorialStep + 1 }}</span>
                <h3 class="card-title">{{ currentTutorialStep.title }}</h3>
              </div>

              <!-- Card Body -->
              <div class="card-body">
                <div class="card-explanation" v-html="currentTutorialStep.explanation"></div>

                <!-- Calculator Section (prominent) -->
                <div v-if="currentTutorialStep.calculator" class="calc-box">
                  <div class="calc-label">🔢 So tippst du es ein:</div>
                  <div class="calc-input-display">
                    <code>{{ currentTutorialStep.calculator }}</code>
                  </div>
                  <div v-if="currentTutorialStep.calcResult" class="calc-result">
                    <span class="equals">=</span>
                    <span class="result-value">{{ currentTutorialStep.calcResult }}</span>
                  </div>
                </div>

                <!-- Formula (compact) -->
                <div v-if="currentTutorialStep.formula" class="formula-compact">
                  <span class="formula-icon">📐</span>
                  <code>{{ currentTutorialStep.formula }}</code>
                </div>

                <!-- Interactive Quiz (fill in the blanks) -->
                <div v-if="currentTutorialStep.quiz && quizAnswers.length > 0" class="quiz-section">
                  <div class="quiz-header">
                    <span class="quiz-icon">✏️</span>
                    <span>Fülle die Lücken aus:</span>
                  </div>
                  <div class="quiz-schema">
                    <div
                      v-for="(item, idx) in currentTutorialStep.quiz"
                      :key="idx"
                      class="schema-row"
                      :class="{
                        'schema-row--result': item.isResult,
                        'schema-row--correct': getQuizAnswer(idx)?.checked && getQuizAnswer(idx)?.correct,
                        'schema-row--wrong': getQuizAnswer(idx)?.checked && !getQuizAnswer(idx)?.correct
                      }"
                    >
                      <span class="schema-operator">{{ item.operator }}</span>
                      <template v-if="item.blank && getQuizAnswer(idx)">
                        <input
                          :value="getQuizAnswer(idx)?.value || ''"
                          @input="setQuizValue(idx, ($event.target as HTMLInputElement).value)"
                          type="text"
                          class="schema-input"
                          :class="{
                            'correct': getQuizAnswer(idx)?.checked && getQuizAnswer(idx)?.correct,
                            'wrong': getQuizAnswer(idx)?.checked && !getQuizAnswer(idx)?.correct
                          }"
                          :placeholder="item.hint || '???'"
                          :disabled="getQuizAnswer(idx)?.checked && getQuizAnswer(idx)?.correct"
                          @keyup.enter="checkQuizAnswer(idx)"
                        />
                        <button
                          v-if="!getQuizAnswer(idx)?.checked || !getQuizAnswer(idx)?.correct"
                          @click="checkQuizAnswer(idx)"
                          class="check-btn"
                        >
                          ✓
                        </button>
                        <span v-if="getQuizAnswer(idx)?.checked" class="answer-feedback">
                          {{ getQuizAnswer(idx)?.correct ? '✅' : '❌' }}
                        </span>
                      </template>
                      <template v-else-if="!item.blank">
                        <span class="schema-text">{{ item.text }}</span>
                      </template>
                    </div>
                  </div>
                  <div v-if="quizComplete" class="quiz-result">
                    <span class="quiz-score">{{ quizCorrectCount }}/{{ quizTotalBlanks }} richtig!</span>
                    <span v-if="quizCorrectCount === quizTotalBlanks" class="quiz-success">🎉 Super!</span>
                  </div>
                </div>
              </div>

              <!-- Tip Footer (if exists) -->
              <div v-if="currentTutorialStep.tip" class="card-tip">
                <span class="tip-icon">💡</span>
                <span class="tip-text">{{ currentTutorialStep.tip }}</span>
              </div>
            </div>

            <!-- Navigation (big, clear buttons) -->
            <div class="tutorial-nav-simple">
              <button
                @click="prevTutorialStep"
                class="nav-btn nav-btn-back"
                :disabled="tutorialStep === 0"
              >
                ← Zurück
              </button>

              <button
                v-if="tutorialStep < tutorialSteps.length - 1"
                @click="nextTutorialStep"
                class="nav-btn nav-btn-next"
              >
                Weiter →
              </button>
              <button
                v-else
                @click="startPracticeAfterTutorial"
                class="nav-btn nav-btn-start"
              >
                Los geht's! 🚀
              </button>
            </div>

            <!-- Quick exit -->
            <button @click="backToMenu" class="skip-link">
              ← Zurück zum Menü
            </button>
          </div>

          <!-- Practice Mode -->
          <div v-else-if="currentMode === 'practice'" class="calculation-area">
            <!-- Tutor Avatar (corner position for practice) -->
            <TutorAvatar
              :visible="tutorVisible"
              :text="tutorText"
              :auto-play="tutorAutoPlay"
              :voice="tutorVoice"
              :mood="tutorMood"
              position="corner-br"
              :show-controls="true"
              @speech-end="onTutorSpeechEnd"
            />

            <!-- Practice Header -->
            <div class="practice-header">
              <div class="practice-info">
                <span class="practice-badge">Aufgabe {{ currentPracticeIdx + 1 }} / {{ practiceCount }}</span>
                <span class="practice-type">{{ getCalculationTitle() }}</span>
              </div>
              <div class="practice-score" v-if="practiceResults.length > 0">
                ✅ {{ practiceResults.filter(r => r >= 80).length }} / {{ practiceResults.length }} bestanden
              </div>
            </div>

            <!-- Question Section -->
            <div class="question-section">
              <div class="question-icon">📝</div>
              <div class="question-content">
                <h3 class="question-title">AUFGABENSTELLUNG</h3>
                <p class="question-text">{{ currentTask.question }}</p>

                <!-- Given Values -->
                <div class="given-values">
                  <h4>Gegebene Werte:</h4>
                  <div class="values-grid">
                    <div
                      v-for="(value, key) in currentTask.givenValues"
                      :key="key"
                      class="value-item"
                    >
                      <span class="value-label">{{ formatLabel(key) }}:</span>
                      <span class="value-number">{{ formatValue(value) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Calculation Table -->
            <div class="calc-table-wrapper">
              <table class="calc-table">
                <thead>
                  <tr>
                    <th class="col-step">Schritt</th>
                    <th class="col-name">Bezeichnung</th>
                    <th class="col-operator">+/-</th>
                    <th class="col-input">Deine Berechnung</th>
                    <th class="col-status">Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(step, index) in calculationSteps"
                    :key="index"
                    :class="getRowClass(step, index)"
                  >
                    <td class="col-step">
                      <span class="step-number">{{ index + 1 }}</span>
                    </td>
                    <td class="col-name">
                      <!-- Normal: Bezeichnungen anzeigen -->
                      <template v-if="!examMode">
                        <span class="step-name">{{ step.name }}</span>
                        <span v-if="step.hint" class="step-hint">{{ step.hint }}</span>
                      </template>
                      <!-- Prüfungsmodus: Input für Bezeichnung -->
                      <template v-else>
                        <input
                          v-if="!hasSubmitted"
                          v-model="examNameInputs[index]"
                          type="text"
                          class="exam-input exam-name-input"
                          :placeholder="'Bezeichnung...'"
                        />
                        <div v-else class="exam-answer">
                          <span class="step-name" :class="{ 'exam-correct': isNameCorrect(index), 'exam-wrong': !isNameCorrect(index) }">
                            {{ step.name }}
                          </span>
                          <span v-if="examNameInputs[index] && !isNameCorrect(index)" class="exam-user-answer">
                            (Deine Antwort: {{ examNameInputs[index] }})
                          </span>
                        </div>
                      </template>
                    </td>
                    <td class="col-operator">
                      <!-- Normal: Operator anzeigen -->
                      <template v-if="!examMode">
                        <span class="operator" :class="step.operator">
                          {{ step.operator === 'minus' ? '−' : step.operator === 'plus' ? '+' : '=' }}
                        </span>
                      </template>
                      <!-- Prüfungsmodus: Input für Operator -->
                      <template v-else>
                        <input
                          v-if="!hasSubmitted"
                          v-model="examOperatorInputs[index]"
                          type="text"
                          class="exam-input exam-operator-input"
                          placeholder="?"
                          maxlength="1"
                        />
                        <span v-else class="operator" :class="{ 'exam-correct': isOperatorCorrect(index), 'exam-wrong': !isOperatorCorrect(index) }">
                          {{ step.operator === 'minus' ? '−' : step.operator === 'plus' ? '+' : '=' }}
                        </span>
                      </template>
                    </td>
                    <td class="col-input">
                      <div class="input-wrapper">
                        <input
                          v-model="userInputs[index]"
                          type="text"
                          class="calc-input"
                          :class="{
                            correct: stepResults[index] === 'correct',
                            incorrect: stepResults[index] === 'incorrect',
                            'follow-error': stepResults[index] === 'follow-error'
                          }"
                          :placeholder="step.placeholder || '0,00'"
                          :disabled="hasSubmitted"
                          @input="formatInput(index)"
                          @keyup.enter="focusNext(index)"
                        />
                        <span class="currency">€</span>
                      </div>
                    </td>
                    <td class="col-status">
                      <span v-if="hasSubmitted" class="status-icon">
                        <template v-if="stepResults[index] === 'correct'">✅</template>
                        <template v-else-if="stepResults[index] === 'incorrect'">❌</template>
                        <template v-else-if="stepResults[index] === 'follow-error'">⚠️</template>
                        <template v-else>⏳</template>
                      </span>
                    </td>
                  </tr>

                  <!-- Result Row -->
                  <tr class="result-row">
                    <td class="col-step">
                      <span class="step-number final">{{ calculationSteps.length + 1 }}</span>
                    </td>
                    <td class="col-name">
                      <!-- Normal: Bezeichnung anzeigen -->
                      <template v-if="!examMode">
                        <strong>{{ getResultLabel() }}</strong>
                      </template>
                      <!-- Prüfungsmodus: Input für Bezeichnung -->
                      <template v-else>
                        <input
                          v-if="!hasSubmitted"
                          v-model="examNameInputs[calculationSteps.length]"
                          type="text"
                          class="exam-input exam-name-input"
                          placeholder="Bezeichnung..."
                        />
                        <div v-else class="exam-answer">
                          <strong :class="{ 'exam-correct': isResultNameCorrect, 'exam-wrong': !isResultNameCorrect }">
                            {{ getResultLabel() }}
                          </strong>
                          <span v-if="examNameInputs[calculationSteps.length] && !isResultNameCorrect" class="exam-user-answer">
                            (Deine Antwort: {{ examNameInputs[calculationSteps.length] }})
                          </span>
                        </div>
                      </template>
                    </td>
                    <td class="col-operator">
                      <!-- Normal: = anzeigen -->
                      <template v-if="!examMode">
                        <span class="operator equals">=</span>
                      </template>
                      <!-- Prüfungsmodus: Input für Operator -->
                      <template v-else>
                        <input
                          v-if="!hasSubmitted"
                          v-model="examOperatorInputs[calculationSteps.length]"
                          type="text"
                          class="exam-input exam-operator-input"
                          placeholder="?"
                          maxlength="1"
                        />
                        <span v-else class="operator" :class="{ 'exam-correct': isResultOperatorCorrect, 'exam-wrong': !isResultOperatorCorrect }">
                          =
                        </span>
                      </template>
                    </td>
                    <td class="col-input">
                      <div class="input-wrapper result">
                        <input
                          v-model="userInputs[calculationSteps.length]"
                          type="text"
                          class="calc-input result-input"
                          :class="{
                            correct: stepResults[calculationSteps.length] === 'correct',
                            incorrect: stepResults[calculationSteps.length] === 'incorrect'
                          }"
                          placeholder="Endergebnis"
                          :disabled="hasSubmitted"
                          @keyup.enter="checkCalculation"
                        />
                        <span class="currency">€</span>
                      </div>
                    </td>
                    <td class="col-status">
                      <span v-if="hasSubmitted" class="status-icon">
                        <template v-if="stepResults[calculationSteps.length] === 'correct'">✅</template>
                        <template v-else>❌</template>
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Score Display (after submission) -->
            <div v-if="hasSubmitted" class="score-section">
              <div class="score-card" :class="scoreClass">
                <div class="score-header">
                  <span class="score-icon">{{ score >= 80 ? '🎉' : score >= 50 ? '👍' : '📚' }}</span>
                  <span class="score-title">Dein Ergebnis</span>
                </div>
                <div class="score-value">{{ score }}%</div>
                <div class="score-details">
                  {{ correctSteps }} von {{ totalSteps }} Schritten richtig
                </div>
                <div v-if="hasFollowErrors" class="follow-error-note">
                  ⚠️ Folgefehler wurden berücksichtigt
                </div>
              </div>

              <!-- Solution Display -->
              <div class="solution-section">
                <button @click="showSolution = !showSolution" class="toggle-solution">
                  <span>{{ showSolution ? '🔽' : '▶️' }} Musterlösung anzeigen</span>
                </button>
                <Transition name="slide">
                  <div v-if="showSolution" class="solution-table">
                    <table class="calc-table solution">
                      <tbody>
                        <tr v-for="(step, index) in calculationSteps" :key="index">
                          <td class="col-name">{{ step.name }}</td>
                          <td class="col-operator">
                            {{ step.operator === 'minus' ? '−' : step.operator === 'plus' ? '+' : '=' }}
                          </td>
                          <td class="col-value">{{ formatCurrency(step.correctValue) }}</td>
                        </tr>
                        <tr class="result-row">
                          <td class="col-name"><strong>{{ getResultLabel() }}</strong></td>
                          <td class="col-operator">=</td>
                          <td class="col-value"><strong>{{ formatCurrency(currentTask.result) }}</strong></td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </Transition>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="action-buttons">
              <button
                @click="backToMenu"
                class="btn-back"
              >
                ⬅️ Zurück zum Menü
              </button>
              <button
                v-if="!hasSubmitted"
                @click="checkCalculation"
                class="btn-check"
                :disabled="!canSubmit"
              >
                ✓ Berechnung prüfen
              </button>
              <button
                v-if="hasSubmitted"
                @click="resetCalculation"
                class="btn-retry"
              >
                🔄 Nochmal versuchen
              </button>
              <button
                v-if="hasSubmitted && currentPracticeIdx < practiceCount - 1"
                @click="nextPracticeTask"
                class="btn-next"
              >
                Nächste Aufgabe ➡️
              </button>
              <button
                v-else-if="hasSubmitted && currentPracticeIdx >= practiceCount - 1"
                @click="showPracticeSummary"
                class="btn-finish"
              >
                🏁 Auswertung
              </button>
              <button v-if="!hasSubmitted" @click="generateNewTask" class="btn-new-small">
                🔀 Andere Aufgabe
              </button>
            </div>

            <!-- Practice Summary -->
            <div v-if="showingSummary" class="practice-summary">
              <div class="summary-header">
                <span class="summary-icon">{{ averageScore >= 80 ? '🎉' : averageScore >= 50 ? '👍' : '📚' }}</span>
                <h3>Übung abgeschlossen!</h3>
              </div>
              <div class="summary-stats">
                <div class="stat">
                  <span class="stat-value">{{ practiceResults.length }}</span>
                  <span class="stat-label">Aufgaben</span>
                </div>
                <div class="stat">
                  <span class="stat-value">{{ practiceResults.filter(r => r >= 80).length }}</span>
                  <span class="stat-label">Bestanden</span>
                </div>
                <div class="stat">
                  <span class="stat-value">{{ averageScore }}%</span>
                  <span class="stat-label">Durchschnitt</span>
                </div>
              </div>
              <div class="summary-actions">
                <button @click="restartPractice" class="btn-restart">
                  🔄 Nochmal üben
                </button>
                <button @click="backToMenu" class="btn-back">
                  🏠 Zurück zum Menü
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="modal-footer">
          <div class="footer-left">
            <button @click="backToMenu" class="btn-menu">
              🏠 Hauptmenü
            </button>
          </div>
          <button @click="$emit('close')" class="btn-close">
            Schließen
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, reactive, nextTick, onMounted } from 'vue'
import TutorAvatar from '@/components/tutor/TutorAvatar.vue'
import { ttsApi } from '@/api/tts.api'

// ============================================================================
// Types
// ============================================================================

interface CalculationStep {
  name: string
  operator: 'plus' | 'minus' | 'equals' | 'none'
  correctValue: number
  hint?: string
  placeholder?: string
  formula?: string
}

interface CalculationTask {
  type: string
  question: string
  givenValues: Record<string, number | string>
  steps: CalculationStep[]
  result: number
}

interface Props {
  methodName?: string
  tokensUsed?: number
  initialType?: string
}

const props = withDefaults(defineProps<Props>(), {
  tokensUsed: 0,
  initialType: ''
})

const emit = defineEmits(['close', 'newTask', 'complete'])

// ============================================================================
// Calculation Types
// ============================================================================

const calculationTypes = [
  {
    id: 'bezugskalkulation',
    name: 'Bezugskalkulation',
    icon: '📦',
    description: 'Vom Listeneinkaufspreis zum Einstandspreis',
    taskCount: 15
  },
  {
    id: 'verkaufskalkulation',
    name: 'Verkaufskalkulation',
    icon: '💰',
    description: 'Vom Einstandspreis zum Verkaufspreis',
    taskCount: 12
  },
  {
    id: 'handelskalkulation',
    name: 'Handelskalkulation',
    icon: '🔄',
    description: 'Komplett: Einkauf bis Verkauf',
    taskCount: 10
  },
  {
    id: 'rueckwaertskalkulation',
    name: 'Rückwärtskalkulation',
    icon: '⬅️',
    description: 'Vom Verkaufspreis zum Einkaufspreis',
    taskCount: 8
  }
]

// ============================================================================
// Tutorial Step Interface
// ============================================================================

interface QuizItem {
  operator: string
  text?: string
  blank?: boolean
  answer?: string | string[]
  hint?: string
  isResult?: boolean
}

interface TutorialStep {
  title: string
  explanation: string
  calculator?: string
  calcResult?: string
  formula?: string
  tip?: string
  quiz?: QuizItem[]
}

// ============================================================================
// State
// ============================================================================

// Multi-select for calculation types
const selectedTypes = ref<string[]>(props.initialType ? [props.initialType] : [])
const selectedType = computed(() => selectedTypes.value[0] || '')
const currentMode = ref<'menu' | 'tutorial' | 'practice' | 'practice-select' | 'guided'>('menu')
const hasSubmitted = ref(false)
const showSolution = ref(false)
const showingSummary = ref(false)

// Tutorial state
const tutorialStep = ref(0)
const tutorialSteps = ref<TutorialStep[]>([])

// Tutor Avatar state
const tutorVisible = ref(false)
const tutorText = ref('')
const tutorMood = ref<'friendly' | 'excited' | 'thinking' | 'encouraging'>('friendly')
const tutorVoice = ref('thorsten')
const tutorAutoPlay = ref(true)
const avatarRef = ref<InstanceType<typeof TutorAvatar> | null>(null)

// Quiz state (for interactive schema)
interface QuizAnswer {
  value: string
  checked: boolean
  correct: boolean
}
const quizAnswers = reactive<QuizAnswer[]>([])

// Practice state
const practiceCount = ref(5)
const currentPracticeIdx = ref(0)
const practiceResults = ref<number[]>([])
const examMode = ref(false) // true = Prüfungsmodus (alles selbst eintippen)
const examNameInputs = reactive<string[]>([]) // Bezeichnungen im Prüfungsmodus
const examOperatorInputs = reactive<string[]>([]) // Operatoren im Prüfungsmodus

const currentTask = ref<CalculationTask>({
  type: '',
  question: '',
  givenValues: {},
  steps: [],
  result: 0
})

const calculationSteps = ref<CalculationStep[]>([])
const userInputs = reactive<string[]>([])
const stepResults = reactive<string[]>([])

// ============================================================================
// Computed
// ============================================================================

const totalSteps = computed(() => calculationSteps.value.length + 1)

const correctSteps = computed(() => {
  return stepResults.filter(r => r === 'correct' || r === 'follow-error').length
})

const hasFollowErrors = computed(() => {
  return stepResults.some(r => r === 'follow-error')
})

const score = computed(() => {
  if (totalSteps.value === 0) return 0
  return Math.round((correctSteps.value / totalSteps.value) * 100)
})

const scoreClass = computed(() => {
  if (score.value >= 80) return 'score-excellent'
  if (score.value >= 60) return 'score-good'
  if (score.value >= 40) return 'score-ok'
  return 'score-poor'
})

const canSubmit = computed(() => {
  // At least the result must be filled
  return userInputs[calculationSteps.value.length]?.trim().length > 0
})

const currentTutorialStep = computed(() => tutorialSteps.value[tutorialStep.value])

const averageScore = computed(() => {
  if (practiceResults.value.length === 0) return 0
  const sum = practiceResults.value.reduce((a, b) => a + b, 0)
  return Math.round(sum / practiceResults.value.length)
})

// Quiz computed
const quizTotalBlanks = computed(() => {
  if (!currentTutorialStep.value?.quiz) return 0
  return currentTutorialStep.value.quiz.filter((q: any) => q.blank).length
})

const quizCorrectCount = computed(() => {
  return quizAnswers.filter(a => a.checked && a.correct).length
})

const quizComplete = computed(() => {
  if (!currentTutorialStep.value?.quiz) return false
  // Check if all blank fields have been checked
  let blankIdx = 0
  for (let i = 0; i < currentTutorialStep.value.quiz.length; i++) {
    if (currentTutorialStep.value.quiz[i].blank) {
      if (!quizAnswers[i]?.checked) return false
      blankIdx++
    }
  }
  return blankIdx > 0
})

// ============================================================================
// Methods
// ============================================================================

const selectCalculationType = (type: string) => {
  selectedType.value = type
}

// Safe accessor for quiz answers
const getQuizAnswer = (idx: number) => {
  return quizAnswers[idx] || null
}

const setQuizValue = (idx: number, value: string) => {
  if (quizAnswers[idx]) {
    quizAnswers[idx].value = value
  }
}

const initQuizAnswers = () => {
  quizAnswers.length = 0
  if (currentTutorialStep.value?.quiz) {
    currentTutorialStep.value.quiz.forEach(() => {
      quizAnswers.push({ value: '', checked: false, correct: false })
    })
  }
}

const checkQuizAnswer = (idx: number) => {
  if (!currentTutorialStep.value?.quiz) return
  if (!quizAnswers[idx]) return

  const quizItem = currentTutorialStep.value.quiz[idx]
  if (!quizItem.blank || !quizItem.answer) return

  const userAnswer = quizAnswers[idx].value.trim().toLowerCase()
  const correctAnswers = Array.isArray(quizItem.answer)
    ? quizItem.answer.map((a: string) => a.toLowerCase())
    : [quizItem.answer.toLowerCase()]

  quizAnswers[idx].checked = true
  quizAnswers[idx].correct = correctAnswers.some(ans =>
    userAnswer === ans || userAnswer.includes(ans) || ans.includes(userAnswer)
  )
}

// ============================================================================
// Type Selection Functions
// ============================================================================

const toggleCalculationType = (typeId: string) => {
  const index = selectedTypes.value.indexOf(typeId)
  if (index === -1) {
    selectedTypes.value.push(typeId)
  } else {
    selectedTypes.value.splice(index, 1)
  }
}

const selectAllTypes = () => {
  selectedTypes.value = calculationTypes.map(t => t.id)
}

const clearSelection = () => {
  selectedTypes.value = []
}

const getTypeName = (typeId: string): string => {
  const type = calculationTypes.find(t => t.id === typeId)
  return type?.name || typeId
}

const totalSelectedTasks = computed(() => {
  return selectedTypes.value.reduce((sum, typeId) => {
    const type = calculationTypes.find(t => t.id === typeId)
    return sum + (type?.taskCount || 0)
  }, 0)
})

const getCalculationTitle = (): string => {
  if (selectedTypes.value.length === 0) return ''
  if (selectedTypes.value.length === 1) {
    return getTypeName(selectedTypes.value[0])
  }
  return `${selectedTypes.value.length} Kalkulationsarten gemischt`
}

// Get a random type from selected types (for mixed practice)
const getRandomSelectedType = (): string => {
  if (selectedTypes.value.length === 0) return 'bezugskalkulation'
  const randomIndex = Math.floor(Math.random() * selectedTypes.value.length)
  return selectedTypes.value[randomIndex]
}

// ============================================================================
// Tutorial & Guided Mode Functions
// ============================================================================

const startTutorial = () => {
  if (selectedTypes.value.length === 0) return
  generateTutorialSteps(selectedType.value)
  tutorialStep.value = 0
  initQuizAnswers()
  currentMode.value = 'tutorial'

  // Start Tutor Avatar
  tutorVisible.value = true
  tutorMood.value = 'friendly'
  speakTutorialStep()
}

// Guided Tutorial where Tutor explains a real task
const startGuidedTutorial = () => {
  if (selectedTypes.value.length === 0) return

  // Generate a real task
  const taskType = getRandomSelectedType()
  generateTask(taskType)
  currentMode.value = 'guided'

  // Start Tutor Avatar with introduction
  tutorVisible.value = true
  tutorMood.value = 'friendly'
  guidedStep.value = 0

  // Generate guided steps based on the task
  generateGuidedSteps()
  speakGuidedStep()
}

// Guided Tutorial State
const guidedStep = ref(0)
const guidedSteps = ref<GuidedStep[]>([])

interface GuidedStep {
  title: string
  speech: string
  highlight?: string // Which part to highlight
  calculator?: string // What to type in calculator
  waitForUser?: boolean
}

const generateGuidedSteps = () => {
  const task = currentTask.value
  const steps: GuidedStep[] = []

  // Introduction
  steps.push({
    title: 'Aufgabe verstehen',
    speech: `Okay, lass uns zusammen eine ${getTypeName(task.type)} durchrechnen! ${task.question}`,
  })

  // Explain given values
  const givenValuesText = Object.entries(task.givenValues)
    .map(([key, val]) => `${key}: ${typeof val === 'number' ? formatCurrency(val) : val}`)
    .join(', ')

  steps.push({
    title: 'Gegebene Werte',
    speech: `Wir haben folgende Werte gegeben: ${givenValuesText}. Diese tragen wir jetzt Schritt für Schritt ins Schema ein.`,
  })

  // Each calculation step
  task.steps.forEach((step, index) => {
    const prevValue = index === 0
      ? Object.values(task.givenValues).find(v => typeof v === 'number') as number
      : task.steps[index - 1]?.correctValue || 0

    let calcExplanation = ''
    let calculatorInput = ''

    if (step.operator === 'minus') {
      // Find the percentage for this step
      const percentKey = Object.keys(task.givenValues).find(k =>
        k.toLowerCase().includes('rabatt') || k.toLowerCase().includes('skonto')
      )
      const percent = task.givenValues[percentKey || ''] || 0

      calcExplanation = `Jetzt rechnen wir den ${step.name}. Wir nehmen ${formatCurrency(prevValue)} und ziehen ${percent}% ab.`
      calculatorInput = `${prevValue} × ${percent} ÷ 100 = ${formatCurrency(prevValue * (percent as number) / 100)} (das ziehen wir ab)`
    } else if (step.operator === 'plus') {
      calcExplanation = `Jetzt addieren wir die ${step.name} dazu.`
    }

    steps.push({
      title: `Schritt ${index + 1}: ${step.name}`,
      speech: calcExplanation || `Als nächstes berechnen wir ${step.name}.`,
      calculator: calculatorInput,
      highlight: `step-${index}`,
    })
  })

  // Final result
  steps.push({
    title: 'Ergebnis',
    speech: `Super! Der ${getResultLabel()} beträgt ${formatCurrency(task.result)}. Das war's! Jetzt kannst du es selbst versuchen.`,
  })

  guidedSteps.value = steps
}

const currentGuidedStep = computed(() => guidedSteps.value[guidedStep.value])

const speakGuidedStep = () => {
  const step = currentGuidedStep.value
  if (!step) return
  tutorText.value = step.speech
}

const nextGuidedStep = () => {
  if (guidedStep.value < guidedSteps.value.length - 1) {
    guidedStep.value++
    tutorMood.value = 'friendly'
    speakGuidedStep()
  }
}

const prevGuidedStep = () => {
  if (guidedStep.value > 0) {
    guidedStep.value--
    speakGuidedStep()
  }
}

const finishGuidedTutorial = () => {
  // Go to practice after guided tutorial
  currentMode.value = 'practice-select'
  tutorText.value = 'Jetzt bist du dran! Wähle wie du üben möchtest.'
  tutorMood.value = 'encouraging'
}

// Tutor Avatar Functions
const speakTutorialStep = () => {
  const step = currentTutorialStep.value
  if (!step) return

  // Generate speech text from tutorial step
  let speechText = step.title + '. '

  // Add explanation (strip HTML)
  if (step.explanation) {
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = step.explanation
    speechText += tempDiv.textContent || tempDiv.innerText || ''
  }

  // Add tip if exists
  if (step.tip) {
    speechText += ' Tipp: ' + step.tip
  }

  tutorText.value = speechText
}

const onTutorSpeechEnd = () => {
  // Speech finished - could auto-advance or wait for user
  tutorMood.value = 'encouraging'
}

const onTutorSkip = () => {
  // User skipped the audio
  tutorMood.value = 'neutral'
}

const showPracticeSelect = () => {
  if (!selectedType.value) return
  currentMode.value = 'practice-select'
}

const startPracticeNormal = () => {
  examMode.value = false
  startPractice()
}

const startPracticeExam = () => {
  examMode.value = true
  startPractice()
}

const startPractice = () => {
  if (selectedTypes.value.length === 0) return
  currentMode.value = 'practice'
  currentPracticeIdx.value = 0
  practiceResults.value = []
  showingSummary.value = false

  // Use random type from selected types (for mixed practice)
  const taskType = getRandomSelectedType()
  generateTask(taskType)

  // Tutor gibt Motivation
  const mixedInfo = selectedTypes.value.length > 1 ? ' Die Aufgaben sind gemischt!' : ''
  if (examMode.value) {
    tutorText.value = `Prüfungsmodus! Zeig was du kannst.${mixedInfo} Du musst alle Felder selbst ausfüllen - Bezeichnungen, Rechenzeichen und Werte. Viel Erfolg!`
    tutorMood.value = 'encouraging'
  } else {
    tutorText.value = `Los gehts!${mixedInfo} Die Bezeichnungen sind schon da, du musst nur noch die Werte berechnen. Du schaffst das!`
    tutorMood.value = 'friendly'
  }
  tutorVisible.value = true
}

const startPracticeAfterTutorial = () => {
  // Nach Tutorial fragen welcher Modus
  currentMode.value = 'practice-select'
  // Tutor verabschiedet sich vom Tutorial
  tutorText.value = 'Super, du hast die Erklärung durchgearbeitet! Jetzt wähle wie du üben möchtest.'
  tutorMood.value = 'excited'
}

const backToMenu = () => {
  currentMode.value = 'menu'
  // Tutor ausblenden
  tutorVisible.value = false
  hasSubmitted.value = false
  showSolution.value = false
  showingSummary.value = false
  userInputs.length = 0
  stepResults.length = 0
  examNameInputs.length = 0
  examOperatorInputs.length = 0
}

// Prüfungsmodus: Check if name is correct
const isNameCorrect = (index: number): boolean => {
  const userAnswer = (examNameInputs[index] || '').trim().toLowerCase()
  const step = calculationSteps.value[index]
  if (!step) return false

  // Extract key terms from step name
  const correctName = step.name.toLowerCase()

  // Check for common abbreviations and terms
  const keyTerms: { [key: string]: string[] } = {
    'listeneinkaufspreis': ['lep', 'listeneinkaufspreis', 'listenpreis'],
    'lieferantenrabatt': ['rabatt', 'lieferantenrabatt'],
    'zieleinkaufspreis': ['zep', 'zieleinkaufspreis', 'zielpreis'],
    'lieferantenskonto': ['skonto', 'lieferantenskonto'],
    'bareinkaufspreis': ['bep', 'bareinkaufspreis', 'barpreis'],
    'bezugskosten': ['bezugskosten', 'fracht', 'transport'],
    'handlungskosten': ['handlungskosten', 'gemeinkosten', 'hk'],
    'selbstkosten': ['selbstkosten', 'sk'],
    'gewinn': ['gewinn', 'gewinnzuschlag'],
    'barverkaufspreis': ['bvp', 'barverkaufspreis'],
    'kundenskonto': ['skonto', 'kundenskonto'],
    'zielverkaufspreis': ['zvp', 'zielverkaufspreis'],
    'kundenrabatt': ['rabatt', 'kundenrabatt'],
    'listenverkaufspreis': ['lvp', 'listenverkaufspreis', 'nettoverkaufspreis'],
    'mwst': ['mwst', 'mehrwertsteuer', 'umsatzsteuer', 'ust', '19%']
  }

  for (const [key, alternatives] of Object.entries(keyTerms)) {
    if (correctName.includes(key)) {
      return alternatives.some(alt => userAnswer.includes(alt))
    }
  }

  // Fallback: direct comparison
  return userAnswer.includes(correctName.split(' ')[0].replace(/[^a-zäöü]/g, ''))
}

// Prüfungsmodus: Check if operator is correct (accepts +, -, = as free text)
const isOperatorCorrect = (index: number): boolean => {
  const step = calculationSteps.value[index]
  if (!step) return false
  const userInput = (examOperatorInputs[index] || '').trim()

  // Map user input to expected operator
  const operatorMap: { [key: string]: string[] } = {
    'plus': ['+'],
    'minus': ['-', '−', '–'],  // Accept different minus characters
    'equals': ['=']
  }

  const validInputs = operatorMap[step.operator] || []
  return validInputs.includes(userInput)
}

// Prüfungsmodus: Check if result name is correct
const isResultNameCorrect = computed((): boolean => {
  const userAnswer = (examNameInputs[calculationSteps.value.length] || '').trim().toLowerCase()
  if (!userAnswer) return false

  // Valid answers depend on calculation type
  const resultTerms: { [key: string]: string[] } = {
    'bezugskalkulation': ['einstandspreis', 'bezugspreis', 'bep', 'ep'],
    'verkaufskalkulation': ['bruttoverkaufspreis', 'bvp', 'brutto', 'verkaufspreis'],
    'handelskalkulation': ['bruttoverkaufspreis', 'bvp', 'brutto', 'verkaufspreis'],
    'rueckwaertskalkulation': ['listeneinkaufspreis', 'lep', 'maximaler einkaufspreis', 'max. einkaufspreis']
  }

  const validTerms = resultTerms[selectedType.value] || []
  return validTerms.some(term => userAnswer.includes(term))
})

// Prüfungsmodus: Check if result operator is correct (always =)
const isResultOperatorCorrect = computed((): boolean => {
  const userInput = (examOperatorInputs[calculationSteps.value.length] || '').trim()
  return userInput === '='
})

const nextTutorialStep = () => {
  if (tutorialStep.value < tutorialSteps.value.length - 1) {
    tutorialStep.value++
    nextTick(() => {
      initQuizAnswers()
      // Tutor speaks the new step
      tutorMood.value = 'friendly'
      speakTutorialStep()
    })
  }
}

const prevTutorialStep = () => {
  if (tutorialStep.value > 0) {
    tutorialStep.value--
    nextTick(() => {
      initQuizAnswers()
      // Tutor speaks the previous step
      tutorMood.value = 'friendly'
      speakTutorialStep()
    })
  }
}

const nextPracticeTask = () => {
  // Save current score
  practiceResults.value.push(score.value)
  currentPracticeIdx.value++
  // Use random type from selected types (for mixed practice)
  const taskType = getRandomSelectedType()
  generateTask(taskType)
}

const showPracticeSummary = () => {
  practiceResults.value.push(score.value)
  showingSummary.value = true
}

const restartPractice = () => {
  currentPracticeIdx.value = 0
  practiceResults.value = []
  showingSummary.value = false
  generateTask(selectedType.value)
}

const generateTask = (type: string) => {
  // Reset state
  hasSubmitted.value = false
  showSolution.value = false
  userInputs.length = 0
  stepResults.length = 0
  examNameInputs.length = 0
  examOperatorInputs.length = 0

  switch (type) {
    case 'bezugskalkulation':
      generateBezugskalkulation()
      break
    case 'verkaufskalkulation':
      generateVerkaufskalkulation()
      break
    case 'handelskalkulation':
      generateHandelskalkulation()
      break
    case 'rueckwaerts':
      generateRueckwaertskalkulation()
      break
    default:
      generateBezugskalkulation()
  }

  // Initialize input fields
  for (let i = 0; i <= calculationSteps.value.length; i++) {
    userInputs[i] = ''
    stepResults[i] = ''
    examNameInputs[i] = ''
    examOperatorInputs[i] = ''
  }
}

const generateBezugskalkulation = () => {
  // Random values
  const stueckzahl = randomInt(50, 200) * 10
  const lepProStueck = randomDecimal(10, 100)
  const rabattProzent = randomChoice([5, 10, 15, 20])
  const skontoProzent = randomChoice([2, 3])
  const bezugskosten = randomInt(50, 300)

  // Calculations
  const lep = stueckzahl * lepProStueck
  const rabatt = lep * (rabattProzent / 100)
  const zep = lep - rabatt
  const skonto = zep * (skontoProzent / 100)
  const bep = zep - skonto
  const einstandspreis = bep + bezugskosten

  currentTask.value = {
    type: 'bezugskalkulation',
    question: `Ein Einzelhändler kauft ${stueckzahl} Stück eines Produkts zum Listeneinkaufspreis von ${formatCurrency(lepProStueck)} pro Stück. Er erhält ${rabattProzent}% Lieferantenrabatt und ${skontoProzent}% Skonto. Die Bezugskosten betragen ${formatCurrency(bezugskosten)}. Berechne den Einstandspreis (Bezugspreis).`,
    givenValues: {
      'Stückzahl': stueckzahl,
      'LEP pro Stück': lepProStueck,
      'Rabatt': `${rabattProzent}%`,
      'Skonto': `${skontoProzent}%`,
      'Bezugskosten': bezugskosten
    },
    steps: [],
    result: round2(einstandspreis)
  }

  calculationSteps.value = [
    { name: 'Listeneinkaufspreis (LEP)', operator: 'none', correctValue: round2(lep), hint: `${stueckzahl} × ${formatCurrency(lepProStueck)}` },
    { name: `− Lieferantenrabatt (${rabattProzent}%)`, operator: 'minus', correctValue: round2(rabatt) },
    { name: '= Zieleinkaufspreis (ZEP)', operator: 'equals', correctValue: round2(zep) },
    { name: `− Lieferantenskonto (${skontoProzent}%)`, operator: 'minus', correctValue: round2(skonto) },
    { name: '= Bareinkaufspreis (BEP)', operator: 'equals', correctValue: round2(bep) },
    { name: '+ Bezugskosten', operator: 'plus', correctValue: round2(bezugskosten) }
  ]
}

const generateVerkaufskalkulation = () => {
  const einstandspreis = randomInt(500, 2000)
  const handlungskostenProzent = randomChoice([20, 25, 30])
  const gewinnProzent = randomChoice([10, 15, 20])
  const kundenskontoProzent = randomChoice([2, 3])
  const kundenrabattProzent = randomChoice([5, 10])
  const mwstProzent = 19

  // Calculations
  const handlungskosten = einstandspreis * (handlungskostenProzent / 100)
  const selbstkosten = einstandspreis + handlungskosten
  const gewinn = selbstkosten * (gewinnProzent / 100)
  const barverkaufspreis = selbstkosten + gewinn
  const kundenskonto = barverkaufspreis / (1 - kundenskontoProzent / 100) - barverkaufspreis
  const zielverkaufspreis = barverkaufspreis + kundenskonto
  const kundenrabatt = zielverkaufspreis / (1 - kundenrabattProzent / 100) - zielverkaufspreis
  const nettoverkaufspreis = zielverkaufspreis + kundenrabatt
  const mwst = nettoverkaufspreis * (mwstProzent / 100)
  const bruttoverkaufspreis = nettoverkaufspreis + mwst

  currentTask.value = {
    type: 'verkaufskalkulation',
    question: `Der Einstandspreis einer Ware beträgt ${formatCurrency(einstandspreis)}. Die Handlungskosten betragen ${handlungskostenProzent}%, der Gewinnzuschlag ${gewinnProzent}%, Kundenskonto ${kundenskontoProzent}%, Kundenrabatt ${kundenrabattProzent}% und MwSt. ${mwstProzent}%. Berechne den Bruttoverkaufspreis.`,
    givenValues: {
      'Einstandspreis': einstandspreis,
      'Handlungskosten': `${handlungskostenProzent}%`,
      'Gewinnzuschlag': `${gewinnProzent}%`,
      'Kundenskonto': `${kundenskontoProzent}%`,
      'Kundenrabatt': `${kundenrabattProzent}%`,
      'MwSt.': `${mwstProzent}%`
    },
    steps: [],
    result: round2(bruttoverkaufspreis)
  }

  calculationSteps.value = [
    { name: 'Einstandspreis (Bezugspreis)', operator: 'none', correctValue: round2(einstandspreis) },
    { name: `+ Handlungskosten (${handlungskostenProzent}%)`, operator: 'plus', correctValue: round2(handlungskosten) },
    { name: '= Selbstkosten', operator: 'equals', correctValue: round2(selbstkosten) },
    { name: `+ Gewinn (${gewinnProzent}%)`, operator: 'plus', correctValue: round2(gewinn) },
    { name: '= Barverkaufspreis', operator: 'equals', correctValue: round2(barverkaufspreis) },
    { name: `+ Kundenskonto (${kundenskontoProzent}%)`, operator: 'plus', correctValue: round2(kundenskonto), hint: 'Im Hundert!' },
    { name: '= Zielverkaufspreis', operator: 'equals', correctValue: round2(zielverkaufspreis) },
    { name: `+ Kundenrabatt (${kundenrabattProzent}%)`, operator: 'plus', correctValue: round2(kundenrabatt), hint: 'Im Hundert!' },
    { name: '= Nettoverkaufspreis (Listenpreis)', operator: 'equals', correctValue: round2(nettoverkaufspreis) },
    { name: `+ MwSt. (${mwstProzent}%)`, operator: 'plus', correctValue: round2(mwst) }
  ]
}

const generateHandelskalkulation = () => {
  // Simplified combined calculation
  const stueckzahl = randomInt(10, 50) * 10
  const lepProStueck = randomDecimal(20, 80)
  const rabattProzent = randomChoice([10, 15, 20])
  const bezugskosten = randomInt(100, 400)
  const gewinnProzent = randomChoice([20, 25, 30])
  const mwstProzent = 19

  const lep = stueckzahl * lepProStueck
  const rabatt = lep * (rabattProzent / 100)
  const einstandspreis = lep - rabatt + bezugskosten
  const gewinn = einstandspreis * (gewinnProzent / 100)
  const nettoverkaufspreis = einstandspreis + gewinn
  const mwst = nettoverkaufspreis * (mwstProzent / 100)
  const bruttoverkaufspreis = nettoverkaufspreis + mwst

  currentTask.value = {
    type: 'handelskalkulation',
    question: `Ein Händler kauft ${stueckzahl} Artikel zum LEP von ${formatCurrency(lepProStueck)}/Stück. Nach ${rabattProzent}% Rabatt und ${formatCurrency(bezugskosten)} Bezugskosten soll ein Gewinn von ${gewinnProzent}% erzielt werden. Berechne den Bruttoverkaufspreis (inkl. ${mwstProzent}% MwSt.).`,
    givenValues: {
      'Stückzahl': stueckzahl,
      'LEP/Stück': lepProStueck,
      'Rabatt': `${rabattProzent}%`,
      'Bezugskosten': bezugskosten,
      'Gewinn': `${gewinnProzent}%`,
      'MwSt.': `${mwstProzent}%`
    },
    steps: [],
    result: round2(bruttoverkaufspreis)
  }

  calculationSteps.value = [
    { name: 'Listeneinkaufspreis (LEP)', operator: 'none', correctValue: round2(lep) },
    { name: `− Rabatt (${rabattProzent}%)`, operator: 'minus', correctValue: round2(rabatt) },
    { name: '= Einkaufspreis nach Rabatt', operator: 'equals', correctValue: round2(lep - rabatt) },
    { name: '+ Bezugskosten', operator: 'plus', correctValue: round2(bezugskosten) },
    { name: '= Einstandspreis', operator: 'equals', correctValue: round2(einstandspreis) },
    { name: `+ Gewinn (${gewinnProzent}%)`, operator: 'plus', correctValue: round2(gewinn) },
    { name: '= Nettoverkaufspreis', operator: 'equals', correctValue: round2(nettoverkaufspreis) },
    { name: `+ MwSt. (${mwstProzent}%)`, operator: 'plus', correctValue: round2(mwst) }
  ]
}

const generateRueckwaertskalkulation = () => {
  const bruttoverkaufspreis = randomInt(50, 200) * 10
  const mwstProzent = 19
  const kundenrabattProzent = randomChoice([10, 15])
  const gewinnProzent = randomChoice([15, 20, 25])
  const handlungskostenProzent = randomChoice([20, 25])

  // Backwards calculation
  const nettoverkaufspreis = bruttoverkaufspreis / (1 + mwstProzent / 100)
  const zielverkaufspreis = nettoverkaufspreis * (1 - kundenrabattProzent / 100)
  const selbstkosten = zielverkaufspreis / (1 + gewinnProzent / 100)
  const einstandspreis = selbstkosten / (1 + handlungskostenProzent / 100)

  currentTask.value = {
    type: 'rueckwaerts',
    question: `Der Bruttoverkaufspreis beträgt ${formatCurrency(bruttoverkaufspreis)} (inkl. ${mwstProzent}% MwSt.). Kundenrabatt ${kundenrabattProzent}%, Gewinnzuschlag ${gewinnProzent}%, Handlungskosten ${handlungskostenProzent}%. Berechne den maximalen Einstandspreis.`,
    givenValues: {
      'Bruttoverkaufspreis': bruttoverkaufspreis,
      'MwSt.': `${mwstProzent}%`,
      'Kundenrabatt': `${kundenrabattProzent}%`,
      'Gewinn': `${gewinnProzent}%`,
      'Handlungskosten': `${handlungskostenProzent}%`
    },
    steps: [],
    result: round2(einstandspreis)
  }

  calculationSteps.value = [
    { name: 'Bruttoverkaufspreis', operator: 'none', correctValue: round2(bruttoverkaufspreis) },
    { name: `− MwSt. (${mwstProzent}%)`, operator: 'minus', correctValue: round2(bruttoverkaufspreis - nettoverkaufspreis), hint: 'Herausrechnen!' },
    { name: '= Nettoverkaufspreis', operator: 'equals', correctValue: round2(nettoverkaufspreis) },
    { name: `− Kundenrabatt (${kundenrabattProzent}%)`, operator: 'minus', correctValue: round2(nettoverkaufspreis - zielverkaufspreis) },
    { name: '= Zielverkaufspreis', operator: 'equals', correctValue: round2(zielverkaufspreis) },
    { name: `− Gewinn (${gewinnProzent}%)`, operator: 'minus', correctValue: round2(zielverkaufspreis - selbstkosten), hint: 'Herausrechnen!' },
    { name: '= Selbstkosten', operator: 'equals', correctValue: round2(selbstkosten) },
    { name: `− Handlungskosten (${handlungskostenProzent}%)`, operator: 'minus', correctValue: round2(selbstkosten - einstandspreis), hint: 'Herausrechnen!' }
  ]
}

// ============================================================================
// Tutorial Generation
// ============================================================================

const generateTutorialSteps = (type: string) => {
  switch (type) {
    case 'bezugskalkulation':
      tutorialSteps.value = [
        {
          title: 'Was ist eine Bezugskalkulation?',
          explanation: `Die Bezugskalkulation berechnet den <strong>Einstandspreis</strong> (auch Bezugspreis genannt). Das ist der Preis, den die Ware tatsächlich kostet, wenn sie im Lager liegt.<br><br>
          <strong>Ausgangspunkt:</strong> Listeneinkaufspreis (LEP)<br>
          <strong>Zielpunkt:</strong> Einstandspreis`,
          tip: 'Der Einstandspreis ist die Basis für alle weiteren Kalkulationen!'
        },
        {
          title: 'Schritt 1: Listeneinkaufspreis (LEP)',
          explanation: `Der <strong>Listeneinkaufspreis</strong> ist der Preis laut Preisliste des Lieferanten.<br><br>
          Bei mehreren Stück: <em>Stückzahl × Preis pro Stück</em>`,
          calculator: '100 × 25 =',
          calcResult: '2.500,00 €',
          formula: 'LEP = Stückzahl × Stückpreis',
          tip: 'Immer erst die Gesamtsumme berechnen, bevor du Rabatte abziehst!'
        },
        {
          title: 'Schritt 2: Lieferantenrabatt abziehen',
          explanation: `Der <strong>Lieferantenrabatt</strong> ist ein Preisnachlass vom Lieferanten (z.B. für Großkunden).<br><br>
          Er wird <strong>vom LEP abgezogen</strong>.`,
          calculator: '2500 × 10 ÷ 100 =',
          calcResult: '250,00 € (Rabatt)',
          formula: 'Rabatt = LEP × Rabatt% ÷ 100',
          tip: 'Alternativ: 2500 × 0,10 = 250'
        },
        {
          title: 'Schritt 3: Zieleinkaufspreis (ZEP)',
          explanation: `Der <strong>Zieleinkaufspreis</strong> ist der Preis nach Abzug des Rabatts.<br><br>
          "Ziel" bedeutet hier: Du hast noch ein Zahlungsziel (z.B. 30 Tage).`,
          calculator: '2500 − 250 =',
          calcResult: '2.250,00 €',
          formula: 'ZEP = LEP − Rabatt'
        },
        {
          title: 'Schritt 4: Lieferantenskonto abziehen',
          explanation: `Das <strong>Skonto</strong> ist ein Preisnachlass für schnelle Zahlung (z.B. innerhalb 10 Tagen).<br><br>
          Skonto wird <strong>vom ZEP</strong> berechnet.`,
          calculator: '2250 × 3 ÷ 100 =',
          calcResult: '67,50 € (Skonto)',
          formula: 'Skonto = ZEP × Skonto% ÷ 100',
          tip: 'Skonto lohnt sich fast immer - rechne nach!'
        },
        {
          title: 'Schritt 5: Bareinkaufspreis (BEP)',
          explanation: `Der <strong>Bareinkaufspreis</strong> ist der Preis bei sofortiger Barzahlung (nach Skonto-Abzug).`,
          calculator: '2250 − 67,50 =',
          calcResult: '2.182,50 €',
          formula: 'BEP = ZEP − Skonto'
        },
        {
          title: 'Schritt 6: Bezugskosten addieren',
          explanation: `<strong>Bezugskosten</strong> sind alle Kosten, um die Ware ins Lager zu bekommen:<br>
          • Transportkosten / Fracht<br>
          • Verpackung<br>
          • Versicherung<br>
          • Zoll (bei Import)`,
          calculator: '2182,50 + 150 =',
          calcResult: '2.332,50 €',
          formula: 'Einstandspreis = BEP + Bezugskosten',
          tip: 'Bezugskosten werden immer ADDIERT!'
        },
        {
          title: 'Zusammenfassung: Das Schema lernen',
          explanation: `<div style="font-family: monospace; background: rgba(0,0,0,0.1); padding: 0.75rem; border-radius: 0.5rem; font-size: 0.9rem; line-height: 1.6;">
            &nbsp;&nbsp;<strong>Listeneinkaufspreis (LEP)</strong><br>
            − Lieferantenrabatt<br>
            ─────────────────────<br>
            = <strong>Zieleinkaufspreis (ZEP)</strong><br>
            − Lieferantenskonto<br>
            ─────────────────────<br>
            = <strong>Bareinkaufspreis (BEP)</strong><br>
            + Bezugskosten<br>
            ─────────────────────<br>
            = <strong style="color: #10b981;">Einstandspreis</strong>
          </div>`,
          tip: 'Präge dir dieses Schema ein! Im nächsten Schritt darfst du es selbst ausfüllen.'
        },
        {
          title: 'Jetzt bist du dran! Fülle das Schema aus',
          explanation: `Trage die richtigen <strong>Begriffe</strong> ein. Tipp: Schau nicht zurück - teste dein Wissen!`,
          quiz: [
            { operator: ' ', text: 'Listeneinkaufspreis (LEP)' },
            { operator: '−', blank: true, answer: ['Lieferantenrabatt', 'Rabatt', 'Lieferanten-Rabatt'], hint: 'Preisnachlass vom Lieferanten' },
            { operator: '=', blank: true, answer: ['Zieleinkaufspreis', 'ZEP', 'Zieleinkaufspreis (ZEP)'], hint: '3 Buchstaben Abkürzung' },
            { operator: '−', blank: true, answer: ['Lieferantenskonto', 'Skonto', 'Lieferanten-Skonto'], hint: 'Für schnelle Zahlung' },
            { operator: '=', blank: true, answer: ['Bareinkaufspreis', 'BEP', 'Bareinkaufspreis (BEP)'], hint: '3 Buchstaben Abkürzung' },
            { operator: '+', blank: true, answer: ['Bezugskosten', 'Bezugskosten / Fracht', 'Fracht', 'Transport'], hint: 'Kosten für Transport etc.' },
            { operator: '=', text: 'Einstandspreis', isResult: true }
          ],
          tip: 'Lerne dieses Schema auswendig - es kommt in jeder IHK-Prüfung vor!'
        }
      ]
      break

    case 'verkaufskalkulation':
      tutorialSteps.value = [
        {
          title: 'Was ist eine Verkaufskalkulation?',
          explanation: `Die Verkaufskalkulation berechnet den <strong>Verkaufspreis</strong> ausgehend vom Einstandspreis.<br><br>
          <strong>Ausgangspunkt:</strong> Einstandspreis (Bezugspreis)<br>
          <strong>Zielpunkt:</strong> Bruttoverkaufspreis (inkl. MwSt.)`,
          tip: 'Hier rechnest du "vorwärts" - vom Einkauf zum Verkauf.'
        },
        {
          title: 'Schritt 1: Handlungskosten aufschlagen',
          explanation: `<strong>Handlungskosten</strong> (auch Gemeinkosten) decken alle Kosten des Betriebs:<br>
          • Miete, Personal, Strom<br>
          • Werbung, Verwaltung<br>
          • Abschreibungen<br><br>
          Sie werden als Prozentsatz auf den Einstandspreis aufgeschlagen.`,
          calculator: '1000 × 25 ÷ 100 =',
          calcResult: '250,00 € (Handlungskosten)',
          formula: 'Handlungskosten = Einstandspreis × HK%',
          tip: 'Die Selbstkosten = Einstandspreis + Handlungskosten'
        },
        {
          title: 'Schritt 2: Gewinn aufschlagen',
          explanation: `Der <strong>Gewinnzuschlag</strong> ist dein Verdienst. Er wird auf die Selbstkosten berechnet.`,
          calculator: '1250 × 15 ÷ 100 =',
          calcResult: '187,50 € (Gewinn)',
          formula: 'Gewinn = Selbstkosten × Gewinn%'
        },
        {
          title: 'Schritt 3: Kundenskonto "im Hundert"',
          explanation: `<strong>Wichtig:</strong> Kundenskonto wird "im Hundert" gerechnet!<br><br>
          Warum? Du willst nach Skonto-Abzug den Barverkaufspreis erhalten.<br><br>
          <strong>Im Hundert:</strong> Teilen durch (100 − Skonto%), dann × 100`,
          calculator: '1437,50 ÷ 97 × 100 =',
          calcResult: '1.481,96 € (Zielverkaufspreis)',
          formula: 'ZVP = BVP ÷ (100 − Skonto%) × 100',
          tip: '"Im Hundert" = Der Prozentsatz bezieht sich auf den Endwert, nicht auf den Ausgangswert!'
        },
        {
          title: 'Schritt 4: Kundenrabatt "im Hundert"',
          explanation: `Auch der <strong>Kundenrabatt</strong> wird "im Hundert" gerechnet.<br><br>
          Nach Abzug des Rabatts soll der Zielverkaufspreis übrig bleiben.`,
          calculator: '1481,96 ÷ 90 × 100 =',
          calcResult: '1.646,62 € (Listenverkaufspreis)',
          formula: 'LVP = ZVP ÷ (100 − Rabatt%) × 100'
        },
        {
          title: 'Schritt 5: MwSt. aufschlagen',
          explanation: `Die <strong>Mehrwertsteuer</strong> wird zum Schluss "auf Hundert" aufgeschlagen (normale Prozentrechnung).`,
          calculator: '1646,62 × 19 ÷ 100 =',
          calcResult: '312,86 € (MwSt.)',
          formula: 'MwSt. = Netto × 19%',
          tip: 'MwSt. wird immer normal "auf Hundert" gerechnet!'
        },
        {
          title: 'Zusammenfassung: Das Schema lernen',
          explanation: `<div style="font-family: monospace; background: rgba(0,0,0,0.1); padding: 0.75rem; border-radius: 0.5rem; font-size: 0.85rem; line-height: 1.6;">
            &nbsp;&nbsp;<strong>Einstandspreis</strong><br>
            + Handlungskosten<br>
            ─────────────────────<br>
            = <strong>Selbstkosten</strong><br>
            + Gewinn<br>
            ─────────────────────<br>
            = <strong>Barverkaufspreis</strong><br>
            + Kundenskonto <em>(im Hundert!)</em><br>
            ─────────────────────<br>
            = <strong>Zielverkaufspreis</strong><br>
            + Kundenrabatt <em>(im Hundert!)</em><br>
            ─────────────────────<br>
            = <strong>Listenverkaufspreis (netto)</strong><br>
            + MwSt. (19%)<br>
            ─────────────────────<br>
            = <strong style="color: #10b981;">Bruttoverkaufspreis</strong>
          </div>`,
          tip: 'Bei Skonto und Rabatt: "Im Hundert" rechnen! Präge dir das Schema ein.'
        },
        {
          title: 'Jetzt bist du dran! Fülle das Schema aus',
          explanation: `Trage die richtigen <strong>Begriffe</strong> ein. Teste dein Wissen!`,
          quiz: [
            { operator: ' ', text: 'Einstandspreis (Bezugspreis)' },
            { operator: '+', blank: true, answer: ['Handlungskosten', 'Gemeinkosten', 'HK'], hint: 'Kosten des Betriebs' },
            { operator: '=', blank: true, answer: ['Selbstkosten', 'SK'], hint: 'Deine eigenen Kosten' },
            { operator: '+', blank: true, answer: ['Gewinn', 'Gewinnzuschlag'], hint: 'Dein Verdienst' },
            { operator: '=', blank: true, answer: ['Barverkaufspreis', 'BVP'], hint: '3 Buchstaben' },
            { operator: '+', blank: true, answer: ['Kundenskonto', 'Skonto'], hint: 'Im Hundert!' },
            { operator: '=', blank: true, answer: ['Zielverkaufspreis', 'ZVP'], hint: '3 Buchstaben' },
            { operator: '+', blank: true, answer: ['Kundenrabatt', 'Rabatt'], hint: 'Im Hundert!' },
            { operator: '=', blank: true, answer: ['Listenverkaufspreis', 'LVP', 'Nettoverkaufspreis', 'Netto'], hint: 'Listenpreis' },
            { operator: '+', blank: true, answer: ['MwSt', 'Mehrwertsteuer', 'MwSt.', 'Umsatzsteuer', '19%', 'USt'], hint: '19% Steuer' },
            { operator: '=', text: 'Bruttoverkaufspreis', isResult: true }
          ],
          tip: 'Merke: Bei der Vorwärtskalkulation wird Skonto und Rabatt "im Hundert" aufgeschlagen!'
        }
      ]
      break

    case 'handelskalkulation':
      tutorialSteps.value = [
        {
          title: 'Die vollständige Handelskalkulation',
          explanation: `Die Handelskalkulation kombiniert Bezugs- und Verkaufskalkulation.<br><br>
          <strong>Vom Lieferanten bis zum Kunden:</strong><br>
          LEP → Einstandspreis → Bruttoverkaufspreis`,
          tip: 'In der IHK-Prüfung oft als "Kalkulation eines Handelsbetriebs" gefragt.'
        },
        {
          title: 'Teil 1: Bezugskalkulation',
          explanation: `Zuerst berechnest du den <strong>Einstandspreis</strong>:<br><br>
          1. LEP berechnen (Stück × Preis)<br>
          2. Rabatt abziehen → ZEP<br>
          3. Skonto abziehen → BEP<br>
          4. Bezugskosten addieren → <strong>Einstandspreis</strong>`
        },
        {
          title: 'Teil 2: Verkaufskalkulation',
          explanation: `Dann berechnest du den <strong>Verkaufspreis</strong>:<br><br>
          1. Handlungskosten aufschlagen → Selbstkosten<br>
          2. Gewinn aufschlagen → Barverkaufspreis<br>
          3. Skonto & Rabatt (im Hundert!) → Listenpreis<br>
          4. MwSt. aufschlagen → <strong>Bruttoverkaufspreis</strong>`
        },
        {
          title: 'Taschenrechner-Tipp: Kettenrechnung',
          explanation: `Viele Rechner können Kettenrechnungen:<br><br>
          <strong>Beispiel Bezugskalkulation:</strong><br>
          100 × 25 = (LEP)<br>
          − 10% = (nach Rabatt)<br>
          − 3% = (nach Skonto)<br>
          + 150 = (Einstandspreis)`,
          calculator: '100 × 25 = 2500 − 10% = 2250 − 3% = 2182,50 + 150 =',
          calcResult: '2.332,50 €',
          tip: 'Teste, ob dein Taschenrechner die Prozent-Taste so unterstützt!'
        }
      ]
      break

    case 'rueckwaerts':
      tutorialSteps.value = [
        {
          title: 'Was ist eine Rückwärtskalkulation?',
          explanation: `Bei der Rückwärtskalkulation kennst du den <strong>Verkaufspreis</strong> und berechnest, wie viel du maximal beim Einkauf bezahlen darfst.<br><br>
          <strong>Ausgangspunkt:</strong> Bruttoverkaufspreis (Marktpreis)<br>
          <strong>Zielpunkt:</strong> Maximaler Einstandspreis`,
          tip: 'Typische Frage: "Wie viel darf die Ware im Einkauf kosten?"'
        },
        {
          title: 'Das Prinzip: Alles rückwärts!',
          explanation: `Du rechnest das Schema von unten nach oben:<br><br>
          • Statt <strong>aufschlagen</strong> → <strong>herausrechnen</strong><br>
          • "Im Hundert" wird zu "vom Hundert"<br>
          • MwSt. herausrechnen: ÷ 1,19`,
          tip: 'Wichtig: "Herausrechnen" ist NICHT das Gleiche wie "abziehen"!'
        },
        {
          title: 'Schritt 1: MwSt. herausrechnen',
          explanation: `Die MwSt. wird <strong>herausgerechnet</strong>, nicht abgezogen!<br><br>
          <strong>Falsch:</strong> 1190 − 19% = 963,90 ❌<br>
          <strong>Richtig:</strong> 1190 ÷ 1,19 = 1000 ✅`,
          calculator: '1190 ÷ 1,19 =',
          calcResult: '1.000,00 € (Netto)',
          formula: 'Netto = Brutto ÷ 1,19',
          tip: 'Merke: Brutto ÷ 1,19 = Netto (nicht Brutto − 19%!)'
        },
        {
          title: 'Schritt 2: Kundenrabatt herausrechnen',
          explanation: `Bei 10% Rabatt bleiben 90% übrig.<br><br>
          Der Netto-Listenpreis sind 100%, der Zielpreis sind 90%.`,
          calculator: '1000 × 90 ÷ 100 =',
          calcResult: '900,00 € (Zielverkaufspreis)',
          formula: 'ZVP = LVP × (100 − Rabatt%) ÷ 100'
        },
        {
          title: 'Schritt 3: Gewinn & Handlungskosten herausrechnen',
          explanation: `Auch Gewinn und Handlungskosten werden "herausgerechnet".<br><br>
          Bei 20% Gewinn: Die Selbstkosten sind der Barverkaufspreis ÷ 1,20`,
          calculator: '900 ÷ 1,20 =',
          calcResult: '750,00 € (Selbstkosten)',
          formula: 'Selbstkosten = BVP ÷ (1 + Gewinn%/100)'
        },
        {
          title: 'Das Ergebnis: Max. Einstandspreis',
          explanation: `Nach allen Abzügen erhältst du den <strong>maximalen Einstandspreis</strong>.<br><br>
          Wenn du mehr bezahlst, machst du Verlust!`,
          tip: 'In der Prüfung: Vergleiche mit dem Angebot des Lieferanten.'
        },
        {
          title: 'Zusammenfassung: Das Prinzip',
          explanation: `<div style="font-family: monospace; background: rgba(0,0,0,0.1); padding: 0.75rem; border-radius: 0.5rem; font-size: 0.9rem; line-height: 1.6;">
            <strong>Rückwärtskalkulation = Umgekehrt rechnen!</strong><br><br>
            Bruttoverkaufspreis<br>
            <strong>÷ 1,19</strong> → MwSt. herausrechnen<br>
            = Listenverkaufspreis (netto)<br>
            <strong>× 0,9</strong> → Bei 10% Rabatt<br>
            = Zielverkaufspreis<br>
            <strong>÷ 1,20</strong> → Bei 20% Gewinn<br>
            = <strong style="color: #10b981;">Max. Einstandspreis</strong>
          </div>`,
          tip: 'Wichtig: Immer ÷ oder × verwenden, nie − oder + wie bei der Vorwärtskalkulation!'
        },
        {
          title: 'Jetzt bist du dran! Trage die Faktoren ein',
          explanation: `Bei: 19% MwSt., 10% Rabatt, 20% Gewinn. Welche Faktoren brauchst du?`,
          quiz: [
            { operator: ' ', text: 'Bruttoverkaufspreis' },
            { operator: '÷', blank: true, answer: ['1,19', '1.19'], hint: 'MwSt.-Faktor' },
            { operator: '=', text: 'Listenverkaufspreis (netto)' },
            { operator: '×', blank: true, answer: ['0,9', '0.9', '90%'], hint: '100% − 10% Rabatt = ?' },
            { operator: '=', text: 'Zielverkaufspreis' },
            { operator: '÷', blank: true, answer: ['1,2', '1.2', '1,20', '1.20'], hint: '100% + 20% Gewinn = ?' },
            { operator: '=', text: 'Max. Einstandspreis', isResult: true }
          ],
          tip: 'Bei der Rückwärtskalkulation: ÷ zum Herausrechnen, × für Prozent-Reste!'
        }
      ]
      break

    default:
      tutorialSteps.value = [{
        title: 'Tutorial',
        explanation: 'Wähle eine Kalkulationsart aus.'
      }]
  }
}

const checkCalculation = () => {
  if (!canSubmit.value) return

  hasSubmitted.value = true
  let previousCorrect = true

  // Check each step
  calculationSteps.value.forEach((step, index) => {
    const userValue = parseGermanNumber(userInputs[index])
    const correctValue = step.correctValue
    const isCorrect = Math.abs(userValue - correctValue) < 0.02

    if (isCorrect) {
      stepResults[index] = 'correct'
    } else if (!previousCorrect && !userInputs[index]?.trim()) {
      // Empty field after error = follow error
      stepResults[index] = 'follow-error'
    } else {
      stepResults[index] = 'incorrect'
      previousCorrect = false
    }
  })

  // Check final result
  const userResult = parseGermanNumber(userInputs[calculationSteps.value.length])
  const isResultCorrect = Math.abs(userResult - currentTask.value.result) < 0.02
  stepResults[calculationSteps.value.length] = isResultCorrect ? 'correct' : 'incorrect'

  // Tutor gives feedback based on score
  const finalScore = score.value
  if (finalScore >= 90) {
    tutorText.value = 'Ausgezeichnet! ' + finalScore + '% richtig - das war fast perfekt! Weiter so!'
    tutorMood.value = 'excited'
  } else if (finalScore >= 70) {
    tutorText.value = 'Gut gemacht! ' + finalScore + '% richtig. Ein paar kleine Fehler, aber insgesamt solide Arbeit!'
    tutorMood.value = 'encouraging'
  } else if (finalScore >= 50) {
    tutorText.value = finalScore + '% richtig. Da geht noch was! Schau dir die roten Felder an und versuch es nochmal.'
    tutorMood.value = 'friendly'
  } else {
    tutorText.value = 'Hmm, ' + finalScore + '% ist noch ausbaufähig. Kein Problem - schau dir die Lösung an und üb weiter!'
    tutorMood.value = 'thinking'
  }

  emit('complete', { score: score.value, type: currentTask.value.type })
}

const resetCalculation = () => {
  hasSubmitted.value = false
  showSolution.value = false
  for (let i = 0; i <= calculationSteps.value.length; i++) {
    userInputs[i] = ''
    stepResults[i] = ''
  }
}

const generateNewTask = () => {
  generateTask(selectedType.value)
}

const getResultLabel = () => {
  switch (currentTask.value.type) {
    case 'bezugskalkulation': return 'Einstandspreis (Bezugspreis)'
    case 'verkaufskalkulation': return 'Bruttoverkaufspreis'
    case 'handelskalkulation': return 'Bruttoverkaufspreis'
    case 'rueckwaerts': return 'Max. Einstandspreis'
    default: return 'Ergebnis'
  }
}

const getRowClass = (step: CalculationStep, index: number) => {
  return {
    'step-equals': step.operator === 'equals',
    'step-correct': stepResults[index] === 'correct',
    'step-incorrect': stepResults[index] === 'incorrect',
    'step-follow-error': stepResults[index] === 'follow-error'
  }
}

// ============================================================================
// Helper Functions
// ============================================================================

const randomInt = (min: number, max: number) => {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

const randomDecimal = (min: number, max: number) => {
  return Math.round((Math.random() * (max - min) + min) * 100) / 100
}

const randomChoice = <T>(arr: T[]): T => {
  return arr[Math.floor(Math.random() * arr.length)]
}

const round2 = (num: number) => {
  return Math.round(num * 100) / 100
}

const formatCurrency = (value: number | string) => {
  const num = typeof value === 'string' ? parseFloat(value) : value
  return num.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €'
}

const formatValue = (value: number | string) => {
  if (typeof value === 'string' && value.includes('%')) return value
  if (typeof value === 'number') return formatCurrency(value)
  return String(value)
}

const formatLabel = (key: string) => {
  return key.replace(/_/g, ' ')
}

const parseGermanNumber = (str: string): number => {
  if (!str) return 0
  // Convert German number format to standard
  const cleaned = str
    .replace(/\s/g, '')
    .replace(/€/g, '')
    .replace(/\./g, '')  // Remove thousand separators
    .replace(/,/g, '.')  // Convert decimal comma to point
  return parseFloat(cleaned) || 0
}

const formatInput = (index: number) => {
  // Auto-format as user types (optional)
}

const focusNext = (index: number) => {
  const nextIndex = index + 1
  if (nextIndex <= calculationSteps.value.length) {
    nextTick(() => {
      const inputs = document.querySelectorAll('.calc-input')
      const nextInput = inputs[nextIndex] as HTMLInputElement
      if (nextInput) nextInput.focus()
    })
  } else {
    checkCalculation()
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  backdrop-filter: blur(4px);
}

.modal-content {
  background-color: var(--color-surface, #ffffff);
  border-radius: 1rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  max-width: 900px;
  width: 100%;
  max-height: 95vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--color-border, #e5e7eb);
  transition: max-width 0.3s ease;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  background: linear-gradient(135deg, var(--color-primary-50, #eff6ff) 0%, var(--color-surface, #ffffff) 100%);
}

:root.dark .modal-header {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, var(--color-surface, #1f2937) 100%);
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text-primary, #111827);
}

.modal-subtitle {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
}

.close-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: var(--color-text-secondary, #6b7280);
  transition: all 0.2s;
  font-size: 1.25rem;
}

.close-btn:hover {
  background-color: var(--color-bg, #f3f4f6);
  color: var(--color-text-primary, #111827);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

/* Type Selector */
.type-selector {
  text-align: center;
}

.selector-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin-bottom: 1.5rem;
}

.type-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.type-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.25rem;
  border: 2px solid var(--color-border, #e5e7eb);
  border-radius: 0.75rem;
  background-color: var(--color-surface, #ffffff);
  transition: all 0.2s;
  cursor: pointer;
  position: relative;
}

.type-card:hover {
  border-color: var(--color-primary, #3b82f6);
  background-color: var(--color-primary-50, #eff6ff);
}

.type-card.active {
  border-color: var(--color-primary, #3b82f6);
  background-color: var(--color-primary-50, #eff6ff);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

:root.dark .type-card:hover,
:root.dark .type-card.active {
  background-color: rgba(59, 130, 246, 0.15);
}

.type-check {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 24px;
  height: 24px;
  background: var(--color-primary, #3b82f6);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: bold;
}

.type-count {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  margin-top: 0.5rem;
  background: var(--color-bg-secondary, #f3f4f6);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

:root.dark .type-count {
  background: var(--color-bg-tertiary, #374151);
}

.type-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.type-name {
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin-bottom: 0.25rem;
}

.type-desc {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  text-align: center;
}

.btn-start {
  padding: 0.875rem 2rem;
  background: linear-gradient(135deg, var(--color-primary, #3b82f6), #2563eb);
  color: white;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.2s;
}

.btn-start:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-start:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Mode Buttons */
/* Quick Select & Selection Summary */
.selector-hint {
  text-align: center;
  color: var(--color-text-secondary, #6b7280);
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.quick-select {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  margin-bottom: 1rem;
}

.quick-btn {
  padding: 0.5rem 1rem;
  background: var(--color-bg-secondary, #f3f4f6);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-primary, #111827);
  cursor: pointer;
  transition: all 0.2s;
}

.quick-btn:hover:not(:disabled) {
  background: var(--color-bg-tertiary, #e5e7eb);
}

.quick-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

:root.dark .quick-btn {
  background: var(--color-bg-tertiary, #374151);
}

.selection-summary {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, var(--color-primary-50, #eff6ff) 0%, var(--color-surface, #ffffff) 100%);
  border: 1px solid var(--color-primary-200, #bfdbfe);
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

:root.dark .selection-summary {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, var(--color-surface, #1f2937) 100%);
  border-color: rgba(59, 130, 246, 0.3);
}

.summary-text {
  font-weight: 600;
  color: var(--color-text-primary, #111827);
}

.summary-count {
  font-size: 0.875rem;
  color: var(--color-primary, #3b82f6);
}

.mode-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-tutorial {
  padding: 0.875rem 2rem;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: white;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.2s;
}

.btn-tutorial:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
}

.btn-tutorial:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Tutorial Area (ADHS-friendly, compact) */
.tutorial-area {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
}

/* Progress Bar */
.progress-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.progress-bar-bg {
  flex: 1;
  height: 6px;
  background-color: var(--color-border, #e5e7eb);
  border-radius: 9999px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #34d399);
  border-radius: 9999px;
  transition: width 0.4s ease;
}

.progress-text {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary, #6b7280);
  min-width: 40px;
  text-align: right;
}

/* Tutorial Card */
.tutorial-card {
  flex: 1;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.75rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: cardSlide 0.25s ease;
}

@keyframes cardSlide {
  from {
    opacity: 0;
    transform: translateX(15px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.card-header {
  padding: 0.875rem 1.25rem;
  background: linear-gradient(135deg, var(--color-primary, #3b82f6), #2563eb);
  color: white;
}

.card-step {
  display: inline-block;
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.85;
  margin-bottom: 0.125rem;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  line-height: 1.3;
}

.card-body {
  flex: 1;
  padding: 1rem 1.25rem;
  overflow-y: auto;
}

.card-explanation {
  font-size: 0.9375rem;
  line-height: 1.65;
  color: var(--color-text-primary, #111827);
  margin-bottom: 1rem;
}

.card-explanation strong {
  color: var(--color-primary, #3b82f6);
}

/* Calculator Box (compact) */
.calc-box {
  background: linear-gradient(135deg, #ecfdf5, #d1fae5);
  border: 1px solid #10b981;
  border-radius: 0.5rem;
  padding: 0.875rem;
  margin-bottom: 0.75rem;
}

:root.dark .calc-box {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.15));
}

.calc-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #059669;
  margin-bottom: 0.5rem;
}

.calc-input-display {
  background-color: var(--color-surface, #ffffff);
  border-radius: 0.375rem;
  padding: 0.625rem 0.75rem;
  margin-bottom: 0.5rem;
}

.calc-input-display code {
  font-family: 'Fira Code', 'Monaco', 'Consolas', monospace;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary, #111827);
}

.calc-result {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.calc-result .equals {
  font-size: 1.125rem;
  color: #059669;
}

.calc-result .result-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: #059669;
}

/* Formula Compact */
.formula-compact {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  background-color: var(--color-bg, #f9fafb);
  border-radius: 0.375rem;
  margin-bottom: 0.75rem;
}

.formula-icon {
  font-size: 0.875rem;
}

.formula-compact code {
  font-family: 'Fira Code', 'Monaco', monospace;
  font-size: 0.8125rem;
  color: var(--color-primary, #3b82f6);
}

/* Card Tip */
.card-tip {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: #fef3c7;
  border-top: 1px solid #fcd34d;
}

:root.dark .card-tip {
  background-color: rgba(251, 191, 36, 0.15);
  border-color: rgba(251, 191, 36, 0.3);
}

.tip-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.tip-text {
  font-size: 0.8125rem;
  color: #92400e;
  line-height: 1.45;
}

:root.dark .tip-text {
  color: #fbbf24;
}

/* Navigation (compact buttons) */
.tutorial-nav-simple {
  display: flex;
  gap: 0.75rem;
}

.nav-btn {
  flex: 1;
  padding: 0.75rem 1rem;
  font-size: 0.9375rem;
  font-weight: 600;
  border-radius: 0.5rem;
  transition: all 0.2s;
  cursor: pointer;
}

.nav-btn-back {
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  color: var(--color-text-secondary, #6b7280);
}

.nav-btn-back:hover:not(:disabled) {
  border-color: var(--color-text-secondary, #9ca3af);
  color: var(--color-text-primary, #111827);
}

.nav-btn-back:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.nav-btn-next {
  background: linear-gradient(135deg, var(--color-primary, #3b82f6), #2563eb);
  border: none;
  color: white;
}

.nav-btn-next:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.nav-btn-start {
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  color: white;
}

.nav-btn-start:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

/* Skip Link */
.skip-link {
  align-self: center;
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
}

.skip-link:hover {
  color: var(--color-text-primary, #111827);
}

/* Practice Header */
.practice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: var(--color-bg, #f9fafb);
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.practice-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.practice-badge {
  padding: 0.25rem 0.75rem;
  background: linear-gradient(135deg, var(--color-primary, #3b82f6), #2563eb);
  color: white;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
}

.practice-type {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
}

.practice-score {
  font-size: 0.875rem;
  font-weight: 600;
  color: #059669;
}

/* Practice Summary */
.practice-summary {
  text-align: center;
  padding: 2rem;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.1));
  border: 2px solid #10b981;
  border-radius: 1rem;
  margin-top: 1.5rem;
}

.summary-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.summary-icon {
  font-size: 3rem;
}

.summary-header h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary, #111827);
}

.summary-stats {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.summary-stats .stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.summary-stats .stat-value {
  font-size: 2rem;
  font-weight: 800;
  color: #059669;
}

.summary-stats .stat-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
}

.summary-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.btn-restart {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-restart:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

/* New buttons */
.btn-next {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-next:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.btn-finish {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-finish:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
}

.btn-new-small {
  padding: 0.5rem 1rem;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  color: var(--color-text-secondary, #6b7280);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-new-small:hover {
  border-color: var(--color-primary, #3b82f6);
  color: var(--color-primary, #3b82f6);
}

/* Question Section */
.question-section {
  display: flex;
  gap: 1rem;
  padding: 1.25rem;
  background-color: var(--color-primary-50, #eff6ff);
  border: 1px solid var(--color-primary-200, #bfdbfe);
  border-radius: 0.75rem;
  margin-bottom: 1.5rem;
}

:root.dark .question-section {
  background-color: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
}

.question-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.question-content {
  flex: 1;
}

.question-title {
  font-weight: 600;
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.question-text {
  font-size: 1rem;
  color: var(--color-text-primary, #111827);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.given-values h4 {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary, #6b7280);
  margin-bottom: 0.5rem;
}

.values-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.value-item {
  display: flex;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  background-color: var(--color-surface, #ffffff);
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

:root.dark .value-item {
  background-color: var(--color-surface-secondary, #374151);
}

.value-label {
  color: var(--color-text-secondary, #6b7280);
}

.value-number {
  font-weight: 600;
  color: var(--color-text-primary, #111827);
}

/* Calculation Table */
.calc-table-wrapper {
  overflow-x: auto;
  margin-bottom: 1.5rem;
}

.calc-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  overflow: hidden;
}

.calc-table th {
  background-color: var(--color-bg, #f9fafb);
  padding: 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary, #6b7280);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  text-align: left;
  border-bottom: 2px solid var(--color-border, #e5e7eb);
}

:root.dark .calc-table th {
  background-color: var(--color-surface-secondary, #374151);
}

.calc-table td {
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  vertical-align: middle;
}

.calc-table tr:last-child td {
  border-bottom: none;
}

.col-step { width: 60px; text-align: center; }
.col-name { width: 40%; }
.col-operator { width: 50px; text-align: center; }
.col-input { width: 35%; }
.col-status { width: 50px; text-align: center; }

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, var(--color-primary, #3b82f6), #2563eb);
  color: white;
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.75rem;
}

.step-number.final {
  background: linear-gradient(135deg, #10b981, #059669);
  width: 32px;
  height: 32px;
  font-size: 1rem;
}

.step-name {
  font-weight: 500;
  color: var(--color-text-primary, #111827);
}

/* Prüfungsmodus Inputs */
.exam-input {
  padding: 0.375rem 0.5rem;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 0.25rem;
  background-color: var(--color-surface, #ffffff);
  color: var(--color-text-primary, #111827);
  font-size: 0.8125rem;
  transition: all 0.2s;
}

.exam-input:focus {
  outline: none;
  border-color: var(--color-primary, #3b82f6);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.exam-name-input {
  width: 100%;
  min-width: 120px;
}

.exam-operator-input {
  width: 50px;
  text-align: center;
  cursor: pointer;
}

.exam-answer {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.exam-user-answer {
  font-size: 0.7rem;
  color: var(--color-text-secondary, #9ca3af);
  font-style: italic;
}

.exam-correct {
  color: #10b981 !important;
}

.exam-wrong {
  color: #ef4444 !important;
}

.step-hint {
  display: block;
  font-size: 0.7rem;
  color: var(--color-primary, #3b82f6);
  font-style: italic;
}

.operator {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  font-weight: 700;
  font-size: 1rem;
}

.operator.minus {
  background-color: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.operator.plus {
  background-color: rgba(16, 185, 129, 0.1);
  color: #059669;
}

.operator.equals {
  background-color: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.calc-input {
  width: 100%;
  padding: 0.5rem 2.5rem 0.5rem 0.75rem;
  border: 2px solid var(--color-border, #e5e7eb);
  border-radius: 0.375rem;
  background-color: var(--color-surface, #ffffff);
  color: var(--color-text-primary, #111827);
  font-size: 0.9rem;
  font-family: 'Fira Code', 'Monaco', monospace;
  text-align: right;
  transition: all 0.2s;
}

.calc-input:focus {
  outline: none;
  border-color: var(--color-primary, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.calc-input:disabled {
  background-color: var(--color-bg, #f3f4f6);
  cursor: not-allowed;
}

.calc-input.correct {
  border-color: #10b981;
  background-color: rgba(16, 185, 129, 0.05);
}

.calc-input.incorrect {
  border-color: #ef4444;
  background-color: rgba(239, 68, 68, 0.05);
}

.calc-input.follow-error {
  border-color: #f59e0b;
  background-color: rgba(245, 158, 11, 0.05);
}

.currency {
  position: absolute;
  right: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  font-size: 0.875rem;
  pointer-events: none;
}

.result-row {
  background-color: var(--color-primary-50, #eff6ff);
}

:root.dark .result-row {
  background-color: rgba(59, 130, 246, 0.1);
}

.result-input {
  font-weight: 700;
  font-size: 1rem;
}

.status-icon {
  font-size: 1.25rem;
}

.step-equals {
  background-color: var(--color-bg, #f9fafb);
}

:root.dark .step-equals {
  background-color: var(--color-surface-secondary, #374151);
}

/* Score Section */
.score-section {
  margin-bottom: 1.5rem;
}

.score-card {
  text-align: center;
  padding: 1.5rem;
  border-radius: 0.75rem;
  margin-bottom: 1rem;
}

.score-excellent {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.15));
  border: 2px solid #10b981;
}

.score-good {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(37, 99, 235, 0.15));
  border: 2px solid #3b82f6;
}

.score-ok {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(217, 119, 6, 0.15));
  border: 2px solid #f59e0b;
}

.score-poor {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(220, 38, 38, 0.15));
  border: 2px solid #ef4444;
}

.score-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.score-icon {
  font-size: 1.5rem;
}

.score-title {
  font-weight: 600;
  color: var(--color-text-primary, #111827);
}

.score-value {
  font-size: 3rem;
  font-weight: 800;
  color: var(--color-text-primary, #111827);
  line-height: 1;
  margin-bottom: 0.5rem;
}

.score-details {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
}

.follow-error-note {
  margin-top: 0.75rem;
  font-size: 0.75rem;
  color: #d97706;
}

/* Solution Section */
.solution-section {
  margin-top: 1rem;
}

.toggle-solution {
  width: 100%;
  padding: 0.75rem;
  background-color: var(--color-bg, #f9fafb);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  font-weight: 500;
  color: var(--color-text-primary, #111827);
  transition: all 0.2s;
  text-align: left;
}

.toggle-solution:hover {
  background-color: var(--color-surface-secondary, #e5e7eb);
}

.solution-table {
  margin-top: 0.75rem;
  padding: 1rem;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
}

.solution-table .calc-table {
  border: none;
}

.solution-table .calc-table td {
  padding: 0.5rem 0.75rem;
  font-family: 'Fira Code', 'Monaco', monospace;
}

.solution-table .col-value {
  text-align: right;
  font-weight: 600;
  color: var(--color-primary, #3b82f6);
}

/* Action Buttons */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-check {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-check:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.btn-check:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-retry {
  padding: 0.75rem 1.5rem;
  background-color: var(--color-surface, #ffffff);
  border: 2px solid var(--color-border, #e5e7eb);
  color: var(--color-text-primary, #111827);
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-retry:hover {
  border-color: var(--color-primary, #3b82f6);
  background-color: var(--color-primary-50, #eff6ff);
}

.btn-new {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, var(--color-primary, #3b82f6), #2563eb);
  color: white;
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-new:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-back {
  padding: 0.75rem 1.5rem;
  background-color: var(--color-surface, #ffffff);
  border: 2px solid var(--color-border, #e5e7eb);
  color: var(--color-text-secondary, #6b7280);
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-back:hover {
  border-color: var(--color-text-secondary, #9ca3af);
  color: var(--color-text-primary, #111827);
  background-color: var(--color-bg, #f9fafb);
}

.btn-menu {
  padding: 0.5rem 1rem;
  background-color: transparent;
  border: 1px solid var(--color-border, #e5e7eb);
  color: var(--color-text-secondary, #6b7280);
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-menu:hover {
  background-color: var(--color-surface, #ffffff);
  border-color: var(--color-primary, #3b82f6);
  color: var(--color-primary, #3b82f6);
}

/* Footer */
.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border, #e5e7eb);
  background-color: var(--color-bg, #f9fafb);
}

.token-info {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
}

.btn-close {
  padding: 0.625rem 1.25rem;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  color: var(--color-text-primary, #111827);
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-close:hover {
  background-color: var(--color-bg, #f3f4f6);
}

/* Slide Transition */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
}

.slide-enter-to,
.slide-leave-from {
  max-height: 500px;
  opacity: 1;
}

/* Quiz Section */
.quiz-section {
  background-color: var(--color-bg, #f9fafb);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-top: 0.75rem;
}

:root.dark .quiz-section {
  background-color: rgba(255, 255, 255, 0.03);
}

.quiz-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin-bottom: 0.75rem;
}

.quiz-icon {
  font-size: 1rem;
}

.quiz-schema {
  font-family: 'Fira Code', 'Monaco', 'Consolas', monospace;
  font-size: 0.8125rem;
  line-height: 1.8;
}

.schema-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s;
}

.schema-row:hover {
  background-color: rgba(59, 130, 246, 0.05);
}

.schema-row--result {
  margin-top: 0.25rem;
  font-weight: 600;
  background-color: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.schema-row--correct {
  background-color: rgba(16, 185, 129, 0.1);
}

.schema-row--wrong {
  background-color: rgba(239, 68, 68, 0.1);
}

.schema-operator {
  width: 1.5rem;
  text-align: center;
  font-weight: 600;
  color: var(--color-text-secondary, #6b7280);
  flex-shrink: 0;
}

.schema-text {
  color: var(--color-text-primary, #111827);
}

.schema-input {
  flex: 1;
  min-width: 120px;
  max-width: 200px;
  padding: 0.375rem 0.625rem;
  font-family: inherit;
  font-size: 0.8125rem;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 0.25rem;
  background-color: var(--color-surface, #ffffff);
  color: var(--color-text-primary, #111827);
  transition: all 0.2s;
}

.schema-input:focus {
  outline: none;
  border-color: var(--color-primary, #3b82f6);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.schema-input.correct {
  border-color: #10b981;
  background-color: rgba(16, 185, 129, 0.1);
  color: #059669;
}

.schema-input.wrong {
  border-color: #ef4444;
  background-color: rgba(239, 68, 68, 0.1);
}

.schema-input:disabled {
  background-color: rgba(16, 185, 129, 0.1);
  cursor: not-allowed;
}

.check-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary, #3b82f6), #2563eb);
  color: white;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.check-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
}

.answer-feedback {
  font-size: 1rem;
  flex-shrink: 0;
}

.quiz-result {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border, #e5e7eb);
}

.quiz-score {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary, #111827);
}

.quiz-success {
  font-size: 1rem;
}

/* Practice Mode Selection */
.practice-select {
  text-align: center;
  padding: 1rem 0;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
  margin-bottom: 1rem;
  transition: color 0.2s;
}

.back-link:hover {
  color: var(--color-primary, #3b82f6);
}

.selector-subtitle {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
  margin-bottom: 1.5rem;
}

.difficulty-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  max-width: 500px;
  margin: 0 auto;
}

.difficulty-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.25rem;
  border: 2px solid var(--color-border, #e5e7eb);
  border-radius: 0.75rem;
  background-color: var(--color-surface, #ffffff);
  transition: all 0.2s;
  cursor: pointer;
  position: relative;
}

.difficulty-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.difficulty-card.easy {
  border-color: #10b981;
}

.difficulty-card.easy:hover {
  background-color: rgba(16, 185, 129, 0.05);
}

.difficulty-card.hard {
  border-color: #f59e0b;
}

.difficulty-card.hard:hover {
  background-color: rgba(245, 158, 11, 0.05);
}

.difficulty-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.difficulty-name {
  font-weight: 600;
  font-size: 1rem;
  color: var(--color-text-primary, #111827);
  margin-bottom: 0.25rem;
}

.difficulty-desc {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  text-align: center;
  line-height: 1.4;
}

.difficulty-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  font-size: 0.625rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  background-color: #10b981;
  color: white;
}

.difficulty-card.hard .difficulty-badge {
  background-color: #f59e0b;
}

/* Multiple-Choice Buttons */
.choice-wrapper {
  width: 100%;
}

.choice-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.choice-btn {
  flex: 1;
  min-width: 70px;
  padding: 0.5rem 0.625rem;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 0.375rem;
  background-color: var(--color-surface, #ffffff);
  color: var(--color-text-primary, #111827);
  transition: all 0.15s;
  cursor: pointer;
}

.choice-btn:hover:not(:disabled) {
  border-color: var(--color-primary, #3b82f6);
  background-color: var(--color-primary-50, #eff6ff);
}

.choice-btn.selected {
  border-color: var(--color-primary, #3b82f6);
  background-color: var(--color-primary, #3b82f6);
  color: white;
}

.choice-btn.correct {
  border-color: #10b981;
  background-color: #10b981;
  color: white;
}

.choice-btn.incorrect {
  border-color: #ef4444;
  background-color: #ef4444;
  color: white;
}

.choice-btn.show-correct {
  border-color: #10b981;
  background-color: rgba(16, 185, 129, 0.1);
  color: #059669;
  font-weight: 600;
}

.choice-btn:disabled {
  cursor: not-allowed;
  opacity: 0.8;
}

.choice-btn.result-choice {
  font-weight: 600;
}

/* Responsive */
@media (max-width: 640px) {
  .type-grid {
    grid-template-columns: 1fr;
  }

  .difficulty-grid {
    grid-template-columns: 1fr;
  }

  .calc-table th,
  .calc-table td {
    padding: 0.5rem;
    font-size: 0.8rem;
  }

  .col-status { display: none; }

  .schema-input {
    min-width: 80px;
    max-width: 150px;
  }

  .choice-buttons {
    flex-direction: column;
  }

  .choice-btn {
    min-width: 100%;
  }
}
/* ============================================================================
   Guided Mode Styles
   ============================================================================ */
.guided-area {
  padding: 1rem 0;
}

.guided-tutor-section {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  border-radius: 1rem;
  border: 1px solid rgba(59, 130, 246, 0.1);
}

.guided-tutor-section :deep(.tutor-avatar) {
  --avatar-size: 100px;
  --bubble-max-width: 400px;
}

.guided-tutor-section :deep(.speech-bubble) {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.guided-tutor-section :deep(.bubble-text) {
  color: #f1f5f9;
  font-size: 1rem;
  line-height: 1.6;
}

.guided-tutor-section :deep(.bubble-pointer) {
  background: #1e293b;
}

.guided-progress {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.guided-progress .progress-bar-bg {
  flex: 1;
}

.guided-card {
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

:root.dark .guided-card {
  background: var(--color-bg-secondary, #1f2937);
}

.guided-card-header {
  margin-bottom: 1rem;
}

.guided-card-header .step-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: var(--color-primary, #3b82f6);
  color: white;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.guided-card-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0;
}

.guided-schema {
  margin-bottom: 1rem;
  overflow-x: auto;
}

.calc-schema-preview {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9375rem;
}

.calc-schema-preview tr {
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  transition: background 0.2s;
}

.calc-schema-preview tr.highlighted {
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%);
  border-left: 3px solid var(--color-primary, #3b82f6);
}

.calc-schema-preview tr.result-row {
  background: var(--color-bg-secondary, #f9fafb);
  border-top: 2px solid var(--color-border, #e5e7eb);
}

:root.dark .calc-schema-preview tr.result-row {
  background: var(--color-bg-tertiary, #374151);
}

.calc-schema-preview td {
  padding: 0.75rem 0.5rem;
}

.calc-schema-preview .schema-step {
  width: 40px;
  text-align: center;
  font-weight: 600;
  color: var(--color-text-secondary, #6b7280);
}

.calc-schema-preview .schema-name {
  min-width: 150px;
}

.calc-schema-preview .schema-operator {
  width: 30px;
  text-align: center;
  font-weight: 600;
}

.calc-schema-preview .schema-value {
  text-align: right;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 500;
}

.calculator-hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: var(--color-bg-secondary, #f3f4f6);
  border-radius: 0.5rem;
  margin-top: 1rem;
}

:root.dark .calculator-hint {
  background: var(--color-bg-tertiary, #374151);
}

.calc-icon {
  font-size: 1.25rem;
}

.calc-label {
  font-weight: 600;
  color: var(--color-text-secondary, #6b7280);
}

.calc-input {
  background: var(--color-surface, #ffffff);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem;
}

:root.dark .calc-input {
  background: var(--color-bg-secondary, #1f2937);
}

.guided-nav {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1rem;
}
</style>
