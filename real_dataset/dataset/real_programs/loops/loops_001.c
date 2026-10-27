// category: loops  (real program 001)
// Codeforces submission 14181797, problem 491/A, GNU C++, 2015-11-10
// https://codeforces.com/contest/491/submission/14181797
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
int a,b,i;int main(){scanf("%d%d",&a,&b);for(i=b+1;i<a+b+2;i++)printf("%d ",i);for(i=b;i>0;i--)printf("%d ",i);}
