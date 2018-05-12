#ifndef QUEUE_H_INCLUDED
#define QUEUE_H_INCLUDED
#include "structs.h"
typedef struct queue *Q;

Q    QueueInit(int dim);
int  QueuePush(Q fifo, Device_t a);
int  QueuePop(Q fifo, Device_t *a);
int  QueueGetSize(Q fifo);
#endif // QUEUE_H_INCLUDED
