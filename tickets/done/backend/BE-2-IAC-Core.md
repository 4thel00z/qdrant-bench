# BE-2: IAC Core (Qdrant Cloud Terraform)

**Role**: Backend/DevOps Engineer
**Context**: We need to programmatically manage Qdrant instances on Qdrant Cloud to save money by reusing instances or spinning them up on demand.

## Requirements
1. Create an Adapter for Infrastructure as Code (IAC).
2. Integrate the Qdrant Cloud Terraform Provider.
3. Implement methods to:
   - Provision a new Qdrant instance.
   - Retrieve connection details (URL, API Key).
   - Destroy/Deprovision an instance.
   - Check if an existing instance can be reused for a sweep.
4. Use `python-terraform` (no need for async here if it does not come out of the box).

## Acceptance Criteria
- [ ] Terraform scripts (`.tf`) for Qdrant Cloud created.
- [ ] Python Adapter can successfully apply/destroy terraform resources.
- [ ] Logic to reuse an instance if it matches the sweep requirements.

