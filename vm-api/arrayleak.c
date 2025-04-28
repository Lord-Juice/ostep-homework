#include<stdlib.h>

int main(int argc, char const *argv[])
{
    int *data = (int *) malloc(100 * sizeof(int));
    free(data);
    printf(data[0]);
    return 0;
}
