## ADDED Requirements

### Requirement: GitHub submission starts a real background analysis
The Operator Client SHALL allow an authorized contributor to start a saved GitHub submission or admit and start a new eligible GitHub issue in one action. The service SHALL atomically link the immutable submission to one ImplementationRun and durable disposition, execute the first real requirements-analysis step independently of its observing clients, and preserve its correlated session, observable history, artifacts and truthful result or failure through the existing public contracts.

#### Scenario: Start a saved GitHub issue or admit and start together (Ticket 02)
- **WHEN** an authorized contributor starts a saved GitHub submission, or enters a new eligible GitHub URL and chooses start
- **THEN** current repository identity, contribution access, the open issue's implementation authorization and the configured agent runtime prerequisites are checked before atomically linking the immutable submission to one ImplementationRun and a durable background disposition
- **AND** redelivery returns the same run and logical first step; a source edit does not replace the admitted work mandate, and an unrelated pre-existing issue run is not silently adopted for new execution

#### Scenario: Observe the first real background step (Ticket 02)
- **WHEN** the independent worker claims an admitted start
- **THEN** it performs a real agent analysis of the retained issue requirements, preserves the assignment, observable messages, tool calls/results, artifacts and actual session identity through the existing Run History boundary, and records a readable result or concrete failure
- **AND** the GUI distinguishes waiting, running, completed first-step analysis and failed execution, without claiming implementation, qualification or full workflow completion from a completed analysis
- **AND** closing the browser or initiating terminal/task does not own or stop execution; reopening after API/worker replacement reads the same run and retained observations, with uncertain external effects reconciled or reported instead of starting a second logical step

#### Scenario: Retain a late first-step response after transport timeout (Ticket 02)
- **WHEN** the worker loses or times out the adapter response after possible delivery
- **THEN** the attempt remains reconcilable, the GUI reports the uncertain outcome, and a replacement worker requests the same operation receipt without starting a second logical step
- **AND** an eventual response supplies the original real session, observations and result to Run History before the step becomes terminal; a later connection refusal does not erase the previously uncertain delivery
