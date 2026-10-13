// category: mixed  (real program 087)
// Codeforces submission 30139027, problem 854/A, GNU C, 2017-09-06
// https://codeforces.com/contest/854/submission/30139027
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
int main(){
int a,b,n;
scanf("%d",&n);
a=n/2;
if(n%2==0){
    a=a-1;
}
b=n-a;
while(((b%3==0)&&(a%3==0))||((b%2==0)&&(a%2==0))){
a=a-1;
b++;
}
printf("%d %d",a,b);
return 0;
}
