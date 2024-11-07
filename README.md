# FSM

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Start the server

```bash
python manage.py runserver
```

### Create a review

```bash
curl -X POST -H "Content-Type: application/json" -d '{"title": "Review title", "text": "Review text", "stage": 1}' http://localhost:8000/api/review/
```

### Approve a review

```bash
curl -X POST -H "Content-Type: application/json" http://localhost:8000/api/reviews/1/transition/approve/
```


### Publish a review

```bash
curl -X POST -H "Content-Type: application/json" http://localhost:8000/api/reviews/1/transition/publish/
```

### Reject a review

```bash
curl -X POST -H "Content-Type: application/json" http://localhost:8000/api/reviews/1/transition/reject/
```
### State Transitions:

1. `approve`: Transitions from `NEW` to `APPROVED` if the user has approval permissions.

2. `reject`: Transitions from `NEW` to `REJECTED` if the user has approval permissions.

3. `publish`: Transitions from `APPROVED` to `PUBLISHED`.

4. `remove`: Transitions from any state to `REMOVED`.

5. `delete`: Transitions from `REMOVED` to a deleted state (effectively removing the review).


### Detailed Breakdown of Transitions:

    approve:

        Source State: ReviewState.NEW

        Target State: ReviewState.APPROVED

        Permission: this.is_approver (checks if the user is a staff member)

        Action: Sets the approver field of the Review to the current user.

    reject:

        Source State: ReviewState.NEW

        Target State: ReviewState.REJECTED

        Permission: this.is_approver (checks if the user is a staff member)

        Action: Sets the approver field of the Review to the current user.

    publish:

        Source State: ReviewState.APPROVED

        Target State: ReviewState.PUBLISHED

        Permission: lambda flow, user: True (no specific permission check, anyone can publish)

        Action: Sets the published field of the Review to the current timestamp.

    remove:

        Source State: fsm.State.ANY (any state)

        Target State: ReviewState.REMOVED

        Permission: lambda flow, user: True (no specific permission check, anyone can remove)

        Action: No specific action, just transitions to the REMOVED state.

    delete:

        Source State: ReviewState.REMOVED

        Permission: lambda flow, user: True (no specific permission check, anyone can delete)

        Action: Deletes the Review object from the database and sets self.review to None.
