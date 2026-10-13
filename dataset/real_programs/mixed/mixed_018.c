// category: mixed  (real program 018)
// Codeforces submission 39617910, problem 996/A, GNU C, 2018-06-24
// https://codeforces.com/contest/996/submission/39617910
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
#include <stdlib.h>
int main() {
    long long int amount;
    long long int count=0;
    scanf("%lld",&amount);
    while(amount>0) {
        if(amount>=100) {
            amount=amount-100;
            count++;
        } else if(amount>=20 && amount<100) {
            amount=amount-20;
            count++;
        } else if(amount>=10 && amount<20) {
            amount=amount-10;
            count++;
        } else if(amount>=5 && amount<10) {
            amount=amount-5;
            count++;
        } else if(amount>=1 && amount<5) {
            amount=amount-1;
            count++;
        }
    }
    printf("%lld",count);
    return 0;
}
