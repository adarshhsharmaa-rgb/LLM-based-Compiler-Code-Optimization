// category: dead_code  (real program 033)
// Codeforces submission 17405823, problem 665/A, GNU C++, 2016-04-20
// https://codeforces.com/contest/665/submission/17405823
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>
#include <cstdio>
#include <cstring>
using namespace std;

int main() {
    int a, b, ta, tb, hh, mm, start, end;
    scanf("%d%d%d%d", &a, &ta, &b, &tb);
    scanf("%d:%d", &hh, &mm);
    start = hh * 60 + mm;
    end = start + ta - 1;
    if (end > 24 * 60 - 1) end = 24* 60 - 1;
    int tmp = start - 5 * 60 - tb;
    if (tmp < 0) tmp = 0;
    else {
        tmp = tmp / b + 1;
    }
    printf("%d\n", (end - 5 * 60) / b + 1 - tmp);
    return 0;
}
