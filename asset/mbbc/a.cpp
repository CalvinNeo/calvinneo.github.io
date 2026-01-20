#include <iostream>
using namespace std;

struct X { };
struct Y { };
struct Z1 {
};
struct Z {
    Z(int x) { }
    Z(Z1 z1) { }
};

template<typename T>
void f(T t){
    printf("main template\n");
}
template<>
void f(int t){
    printf("spec template of int\n");
}
template<>
void f(Y t){
    printf("spec template of Y\n");
}
template<>
void f(Z t){
    printf("spec template of Z\n");
}
void f(int t){
    printf("normal\n");
}
template<>
void f(double t){
    printf("normal cast\n");
}

template<int I>
void div(double x, char(*)[I % 2 == 0] = 0)
{
    // this overload is selected when I is even
    printf("double\n");
}
 
template<int I>
void div(int y, char(*)[I % 2 == 1] = 0)
{
    // this overload is selected when I is odd
    printf("int\n");
}
 
int main() {
    f(1); // normal
    f(2.0); // normal cast
    f(X{}); // main template
    f(Y{}); // spec template of Y
    f(Z{1}); // spec template of Z
    f(Z1{}); // main template
    f((Z)Z1{}); // spec template of Z
    div<1>(1); // int
    div<2>(2); // int
    return 0;
}