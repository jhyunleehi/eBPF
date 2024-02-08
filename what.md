# 궁금하다

### designated initializer 

"designated initializers(지정된 초기화자)"는 C 언어에서 구조체(struct)를 초기화할 때, 특정 멤버에 대한 초기화를 명시적으로 지정할 수 있는 기능입니다. 이 기능을 사용하면 구조체의 각 멤버를 명확하게 지정하여 초기화할 수 있습니다.

```c
struct Point {
    int x;
    int y;
};

struct Point p1 = {.x = 10, .y = 20};

```
여기서 .x와 .y는 designated initializers입니다. 이를 통해 p1 구조체의 x 멤버와 y 멤버에 각각 10과 20을 할당합니다.

이러한 designated initializers는 코드를 더 읽기 쉽고, 구조체의 멤버가 많거나 일부 멤버에 기본값이 있을 때 유용합니다. 또한, 구조체의 멤버를 원하는 순서대로 초기화할 수 있어서 편리합니다.

designated initializers는 C99 표준에서 소개되었으며, 현대의 C 컴파일러에서 널리 지원됩니다.