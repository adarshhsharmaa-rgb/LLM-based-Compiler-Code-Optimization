// category: repeated_expr  (real program 011)
// Codeforces submission 43309199, problem 1030/D, GNU C++11, 2018-09-23
// https://codeforces.com/contest/1030/submission/43309199
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
#include <algorithm>
#include <string.h>
#include <iostream>
#include <stdlib.h>
using namespace std;

long long a,b,c;

int main(){
	scanf("%lld %lld %lld", &a, &b, &c);
	long long NA=a,NB=b;
	if(a * b * 2 / c * c != a * b * 2) {
		printf("NO\n");
		return 0;
	}else {
		a*=2;b*=2;
		for(int i = 2; i * i <= c; i++){
			while(c%i==0){
				if(a%i==0)a/=i;
				else b/=i;
				c/=i;
			}
		}if(a%c==0)a/=c;
		else b/=c;
		if(a>NA)a/=2;
		else if(b>NB)b/=2;
		else if(a%2==0)a/=2;
		else b/=2;
		printf("YES\n");
		printf("0 0\n");
		printf("0 %lld\n",b);
		printf("%lld 0\n",a);
	}return 0;
}
