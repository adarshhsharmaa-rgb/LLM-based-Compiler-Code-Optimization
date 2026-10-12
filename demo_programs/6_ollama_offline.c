// Sample 6: for the offline demo with the local Ollama model.
// The condition below is always true, but the rules do not remove branches,
// so after them a test and a jump are still left. A small local model can
// finish the job: it should replace the whole program by "print 7", and the
// verifier checks that it got it right.
#include <stdio.h>

int main() {
    int level = -9;
    int score = 0;
    if (level != 5) {
        int unused = 20 + 15;
        score = 0 + level;
        score = score + (4 * 4);
    }
    printf("%d\n", score);
    return 0;
}
