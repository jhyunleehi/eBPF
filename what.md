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


### clang llvm

#### LLVM 이란?
LLVM은 Low Level Virtual Machine의 약자로, 그대로 해석하면 저급 가장 기계라는 뜻으로 2000년에 시작하게 되었다고 한다. 하지만 점점 기능이 많아지면서 프로젝트 자체의 이름으로 사용되게 된다.

LLVM은 컴파일러 인프라스트럭처이다. LLVM을 이용해서 컴파일을 한다. LLVM 내에는 여러 프로젝트가 있는데 대표적으로 LLVM Code와 Clang 등이 있다.

#### Clang이란?
Clang(클랭) 이란 C, C++, Objective-C, Objective-C++ 언어를 컴파일하기 위한 LLVM에 속한 프런트엔드 컴파일러이다.

GCC와 호환되며 더 나은 진단, 더 나은 IDE Integration, 상용 프로덕트와 호환되는 라이센스, 빠르고 사용하기 쉬운 컴파일러를 지향해서 만들게 되었다고 한다.

타깃은 X86-32, X86-64, ARM 등을 지원하며 실제로 Chrome이나 Firefox 같은 성능에 크리티컬 한 소프트웨어의 빌드에도 사용된다고 한다.


#### GCC와 Clang의 차이점
일단 기본적으로 GCC는 더 많은 언어를 지원한다. Clang에서 지원하는 C/C++/Objective-C/Objective-C++ 외에 Java/Ada/Fortran/Go 등을 지원한다. 즉 Clang이 이름 그대로 C언어에 특화되어 있는 것이다.

GCC가 더 많은 아키텍처, 프로세서를 지원한다.
Clang은 GCC에 비해 컴파일 속도가 빠르고 메모리 사용량이 적다. 라이브러리 기반의 모듈식 디자인으로 IDE 통합이 용이하고 더 나은 오류 진단을 제공한다. (Clang을 개발한 목적)
제일 중요한 문제일 수가 있는데, 바로 라이센스가 다르다. Clang은 BSD와 유사한 LLVM 아파치 2 라이선스를 사용하고  GCC는 GPLv3이다.

GPL을 따르는 GCC를 사용한다면 소스코드를 공개해야돼서 실제 상용코드에 사용하기 힘들 수 있다.

 

종합하면, GCC는 더 오래되었고 더 안정적이며 더 많은 언어와 아키텍처에 호환되지만 Clang에 비해 느리고 메모리 사용량이 많을 수 있다. 또한 소스코드를 공개해야 하며 엄격한 규칙을 따라야 하는 GPL을 따르기 때문에 Clang을 사용하는 게 나을 때도 있을 것 같다.