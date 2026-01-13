# Learning Methods Domain Migration Note

**Datum:** 2026-01-08
**Status:** PARTIAL - Needs full DDD refactor
**Token Limit:** Hit at ~100K, continued in next session

---

## Current Status

**OLD LOCATION:**
- `admin/learning_methods/` (~500 LOC, 6 files)
- `admin/lm_routing/` (~2010 LOC, 16 files in 4 subdirectories)

**NEW LOCATION:**
- `system_features/learning_methods/`

**TOTAL COMPLEXITY:** ~2500 LOC - Too large for single session!

---

## What Was Migrated (This Session)

### Core Domain (Created)
- `core/value_objects.py` - Basic value objects (LearningMethodType, MethodStatus)
- `core/__init__.py` - Barrel exports

### Admin Layer (Minimal Structure)
- `admin/__init__.py` - Blueprint placeholders

### What Was NOT Migrated Yet

**High Priority:**
1. **Instances** (`learning_methods/instances.py` - 290 LOC)
   - GET /chapters/{id}/learning-methods
   - GET /learning-methods/{id}
   - POST, PUT, DELETE for instances

2. **Routing** (`lm_routing/` subdirectories - 2010 LOC)
   - `routing/overview.py` - GET overview, unconfigured, requirements
   - `routing/resolution.py` - POST resolve (which model to use)
   - `assignment/assignments.py` - GET/PUT/DELETE assignments
   - `assignment/bulk.py` - POST bulk operations
   - `routing/recommendation_*.py` - Recommendation logic (440 LOC split across 2 files)
   - `setup/ai_setup.py` - POST ai-auto-setup (282 LOC)
   - `slots/` - Capability slots (3 files, ~450 LOC)

3. **Types** (`learning_methods/types.py` - 70 LOC)
   - GET /learning-method-types

4. **Operations** (`learning_methods/operations.py` - 180 LOC)
   - POST /reorder, /publish, /unpublish

---

## Next Session Tasks

1. Complete Core Domain:
   - Factory: LearningMethodInstanceFactory, RoutingConfigFactory
   - Services: MethodValidationService, RoutingResolutionService
   - Events: InstanceCreatedEvent, RoutingChangedEvent

2. Migrate Admin Layer:
   - instances/ (CRUD for learning method instances)
   - types/ (learning method types)
   - operations/ (reorder, publish)
   - routing/ (assignment, resolution, recommendations)
   - slots/ (capability slots)

3. Create Proper DDD Structure:
   ```
   learning_methods/
   ├── core/
   │   ├── value_objects.py
   │   ├── factory.py
   │   ├── services.py
   │   └── events.py
   ├── admin/
   │   ├── instances/
   │   ├── types/
   │   ├── operations/
   │   ├── routing/
   │   └── slots/
   └── __init__.py
   ```

4. Update imports across codebase

5. Delete old admin/learning_methods/ and admin/lm_routing/

---

## Architecture Notes

**Domain:** Learning Methods (12 Content-LMs LM00-LM11)
**Subdomain:** Routing (AI Model Assignment)

**Business Rules:**
- 12 Content-Lernmethoden (LM00-LM11) in 3 groups (A-C)
- Each LM can be assigned to specific AI models
- Routing resolution determines which model to use
- Capability slots for multi-model support
- Instances can be published/unpublished
- Chapter-level reordering

---

**Reference Documents:**
- `LernsystemX-Doku/01_Core/02_Lernmethoden.md` - 12 Content-LMs
- `ARCHITECTURE_REFACTOR_MASTER_PLAN.md` - Overall plan

**Priority:** HIGH - Core feature, must complete in next session!
