// category: mixed  (real program 077)
// Codeforces submission 13664116, problem 53/C, GNU C++, 2015-10-16
// https://codeforces.com/contest/53/submission/13664116
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main(){
    int n;
    scanf("%d",&n);
    
    int i,k=0;
    for(i=1;i<=n;i++){
        if(i%2==1) k++;
        printf("%d ",k);
        k=n+1-k;
    }
}
