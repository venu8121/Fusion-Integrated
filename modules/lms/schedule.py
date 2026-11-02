BEAT_SCHEDULE={"lms-process-scheduled-content":{"task":"lms.process_scheduled_content","schedule":60.0,"options":{"expires":55}}}
TASK_ROUTES={"lms.process_scheduled_content":{"queue":"default"}}
