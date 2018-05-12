#include <stdio.h>
#include <stdlib.h>
#include "queue.h"

typedef struct elemento *link;

struct elemento{
	Device_t V;
    link next;
};

struct queue{
    link head;
    int dim;
    int N;
};

Q QueueInit(int dim)
{
    Q fifo = malloc(sizeof(*fifo));
    fifo->head = NULL;
    fifo->dim = dim;
    fifo->N = 0;
    return fifo;
}
int QueuePush(Q fifo, Device_t a)
{
    link elem, nav;
    if (fifo->N < fifo->dim)
    {
        elem = malloc(sizeof(*elem));
        elem->V = a;
        elem->next = NULL;
        if (fifo->head != NULL)
        {
            nav = fifo->head;
            while (nav->next != NULL)
                nav = nav->next;
            nav->next = elem;
        }
        else
            fifo->head = elem;
        fifo->N++;
        return 1;
    }
    return 0;
}
int QueuePop(Q fifo, Device_t *a)
{
    link elem;
    if (fifo->N > 0)
    {
        *a = fifo->head->V;
        elem = fifo->head;
        fifo->head=fifo->head->next;
        free(elem);
        fifo->N--;
        return 1;
    }
    return 0;
}

int  QueueGetSize(Q fifo) {
	return fifo->N;
}





















