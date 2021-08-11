#include <iostream>
using namespace std;

template<typename T>
void f(T t){
	printf("1");
}
template<>
void f(int t){
	printf("2");
}
void f(int t){
	printf("3");
}
template<>
void f(double t){
	printf("4");
}
 
struct X{};
 
int main() {
	f(1);
	f(2.0);
	f(X{});
	return 0;
}