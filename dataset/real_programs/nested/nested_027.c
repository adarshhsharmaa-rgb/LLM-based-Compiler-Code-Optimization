// category: nested  (real program 027)
// Codeforces submission 20164023, problem 486/A, GNU C++11, 2016-08-25
// https://codeforces.com/contest/486/submission/20164023
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>

using namespace std;

int main()

{

    long long n;scanf("%I64d",&n);

    printf("%I64d",n/2-n*(n%2));

    return 0;

}
