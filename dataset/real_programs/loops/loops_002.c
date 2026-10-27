// category: loops  (real program 002)
// Codeforces submission 2062139, problem 171/G, GNU C++, 2012-08-28
// https://codeforces.com/contest/171/submission/2062139
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
int main (){
    int a,b,c,temp,i;
    scanf("%d %d %d",&a,&b,&c);
    for (i=1;i<c;i++){
        temp=a;
        a=b;
        b=a+temp;
    }
    printf("%d\n",b);
    return 0;
}
