// category: repeated_expr  (real program 001)
// Codeforces submission 8279645, problem 301/C, GNU C++, 2014-10-17
// https://codeforces.com/contest/301/submission/8279645
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
// by ξ

#include <cstdio>

using namespace std;

int main(){
	for(int i=0;i<=9;++i)printf("??%d>>%d??\n",i,i);
	for(int i=0;i<9;++i)printf("%d??<>%d\n",i,i+1);
	puts("9??>>?0");
	puts("9?>>?0");
	for(int i=0;i<9;++i)printf("%d?<>%d\n",i,i+1);
	puts("?<>1");
	puts(">>??");
}
