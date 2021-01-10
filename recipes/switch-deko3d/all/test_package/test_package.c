#include "deko3d.h"

#include <stddef.h>

int main() {
    DkDevice device;
    device = dkDeviceCreate(NULL);
    dkDeviceDestroy(device);
    return 0;
}
