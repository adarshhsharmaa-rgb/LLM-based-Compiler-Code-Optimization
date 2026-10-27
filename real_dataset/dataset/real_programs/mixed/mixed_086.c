// category: mixed  (real program 086)
// Codeforces submission 20571309, problem 124/A, C++14 (GCC 6-32), 2016-09-13
// https://codeforces.com/contest/124/submission/20571309
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

using namespace std;

int main() {
    int n, a, b, x = 0;
    scanf("%d %d %d", &n, &a, &b);
    for (int i = 1; i <= n; ++i) if (i > a && n - i <= b) x++;
    printf("%d", x);
}




//#include <bits/stdc++.h>
//
//using namespace std;
//typedef long long ll;
//ll n, q, a, len;
//char s[1000001], c;
//int rep[28][1000001] = {0};
//
//void make(char *s) {
//    for (int i = 0; i < len; ++i) {
//        rep[s[i] - 'A'][i]++;
//        for (int j = i + 1; j < len; ++j) {
//            rep[s[i] - 'A'][j] += rep[s[i] - 'A'][j - 1];
//        }
//    }
//}
//
//ll getEnd(ll next) {
//    ll end = next % len;
//    if (end == 0) return len;
//    else return end - 1;
//}
//
//ll getAns(char c, ll line) {
//    ll prev = (line * (line - 1)) / 2, next = (line * (line + 1)) / 2;
//    ll wordCnt, ans = 0;
//    if (line > len) {
//        ll st = prev % len;
//        ll end = getEnd(next);
//        wordCnt = abs(next - prev - (len - st)) / len;
//        ans = wordCnt * rep[c - 'A'][len] + rep[c - 'A'][st] - rep[c - 'A'][len] + rep[c - 'A'][end];
//    } else {
//        ll st = prev % len;
//        ll end = getEnd(next);
//        ans = rep[c - 'A'][end] - rep[c - 'A'][st];
//    }
//    return ans;
//}
//
//int main() {
//    scanf("%lld %s %lld", &n, s, &q);
//    len = strlen(s);
//    make(s);
//    while (q--) {
//        scanf("%lld %c", &a, &c);
//        printf("%lld\n", getAns(c, a));
//    }
//}
