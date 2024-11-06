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



