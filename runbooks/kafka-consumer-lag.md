# Kafka Consumer Lag

Service: order-events
Team: messaging

## Symptoms

- Kafka consumer lag continues to increase.
- Order events are processed slowly.
- Messages remain in the topic backlog.

## Investigation

1. Check consumer-group lag and partition distribution.
2. Confirm that consumer pods are healthy.
3. Review logs for processing failures or rebalancing.
4. Scale consumers according to the approved procedure.