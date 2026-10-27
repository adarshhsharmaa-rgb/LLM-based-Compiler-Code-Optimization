// category: mixed  (real program 010)
// Codeforces submission 19519780, problem 690/A2, GNU C++11, 2016-07-30
// https://codeforces.com/contest/690/submission/19519780
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

#include <algorithm>

#include <vector>

using namespace std;

int main()

{

    int n;

    scanf("%d", &n);

    if(n%2==1) printf("%d", n/2);

    else{

        int pow=1;

        while(pow*2<=n) pow*=2;

        printf("%d\n", (n-pow)/2);

    }

    return 0;

}
