# Checkout API 5xx Errors

Service: checkout-api
Team: payments

## Symptoms

- Checkout requests return HTTP 500 or 503 errors.
- The checkout error rate alert is firing.
- Failures may begin after a deployment.

## Investigation

1. Check checkout-api pod health and recent deployments.
2. Review application logs for database or dependency errors.
3. Compare the error-rate increase with the deployment timeline.
4. Follow the approved rollback procedure when appropriate.