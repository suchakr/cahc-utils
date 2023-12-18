#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdarg.h>
#include "z.h"

int foo(int a, int b) { return a + b; } // caller cleans up the stack
int bar(int a, int b) { return a + b; } // callee cleans up the stack
int baz(int a, int b) { return a + b; } // callee cleans up the stack (register-based calling convention)
// inline int bax(int a, int b) { return a + b; } // inline function (compiler optimization)

// a variable args function accepts any number of int arguments and returns their sum
int summer(int n, ...) {
    int sum = 0;
    va_list args;
    va_start(args, n);
    for (int i = 0; i < n; i++) {
        sum += va_arg(args, int);
    }
    va_end(args);
    return sum;
}

void softmax_exp(float *x, int n) { // n is the size of x, i.e., n = sizeof(x) / sizeof(float) at the call site
    // find max value (for numerical stability)
    float max = x[0];
    for (int i = 1; i < n; i++) {
        if (x[i] > max) {
            max = x[i];
        }
    }
    // compute sum of exp(x[i] - max)
    float sum = 0;
    for (int i = 0; i < n; i++) {
        // sum += exp(x[i] - max);
        sum += ( x[i] = exp(x[i] - max));
    }
    // compute softmax
    for (int i = 0; i < n; i++) {
        // x[i] = exp(x[i] - max) / sum;
        x[i] /= sum;
    }
}

void softmax_expf(float* x, int size) {
    // find max value (for numerical stability)
    float max_val = x[0];
    for (int i = 1; i < size; i++) {
        if (x[i] > max_val) {
            max_val = x[i];
        }
    }
    // exp and sum
    float sum = 0.0f;
    for (int i = 0; i < size; i++) {
        x[i] = expf(x[i] - max_val);
        sum += x[i];
    }
    // normalize
    for (int i = 0; i < size; i++) {
        x[i] /= sum;
    }
}

void test_softmax( void softmax(float*, int), float* x, int n , char *tag) {
    softmax(x, n);
    printf("%s => ", tag);
    for (int i = 0; i < n; i++) {
        printf("%f ", x[i]);
    }
    printf("\n");
}

void time_softmax( void softmax(float*, int), float* x, int n, int repeat , char *tag)  {
    clock_t start = clock();
    for (int i = 0; i < repeat; i++) {
        softmax(x, n);
    }
    clock_t end = clock();
    printf("%s => time: %f secs\n", tag, (double)(end - start) / CLOCKS_PER_SEC);
}

void time_adders( int adder(int, int), int a, int b, int repeat , char *tag)  {
    clock_t start = clock();
    for (int i = 0; i < repeat; i++) {
        adder(a, b) ;
    }
    clock_t end = clock();
    printf("%s => time: %f secs\n", tag, (double)(end - start) / CLOCKS_PER_SEC);
}

int do_say2(char *s) {
    printf("%s\n", s);
    return 0;
}

int main2() {
    float x[] = {1, 1, 2, 3, 4};
    if (0) {
        test_softmax(softmax_exp, x, sizeof(x) / sizeof(float), "exp ");
        test_softmax(softmax_expf, x, sizeof(x) / sizeof(float), "expf");
        printf ("====================\n\n");

        time_softmax(softmax_exp, x, sizeof(x) / sizeof(float), 1e8, "exp");
        time_softmax(softmax_expf, x, sizeof(x) / sizeof(float), 1e8, "expf");
        printf ("====================\n\n");

        time_adders(foo, 1, 2, 1e8, "foo_cdecl");
        time_adders(bar, 1, 2, 1e8, "bar_stdcall");
        time_adders(baz, 1, 2, 1e8, "baz_fastcall");
        time_adders(NULL, 1, 2, 1e8, "bax_inline");
        time_adders(summer, 1, 2, 1e8, "summer_varargs");
        printf ("====================\n\n");
    }

    do_say2("Hello, World! - All is well2.\n");
    do_say("Hello, World! - All is well.\n");

    return 0;
}

struct poly {
    int n;
    float *coeffs;
};

struct poly *poly_new(int n, ...) {
    struct poly *p = malloc(sizeof(struct poly));
    p->n = n;
    p->coeffs = malloc(n * sizeof(float));
    va_list args;
    va_start(args, n);
    for (int i = 0; i < n; i++) {
        p->coeffs[i] = va_arg(args, double);
    }
    va_end(args);
    return p;
}  

void poly_free(struct poly *p) {
    free(p->coeffs);
    free(p);
}

void poly_print(struct poly *p) {
    printf("p(x) = ");
    for (int i = 0; i < p->n; i++) {
        printf("%f x^%d ", p->coeffs[i], i);
        if (i < p->n - 1) {
            printf("+ ");
        }
    }
    printf("\n");
}

float poly_eval(struct poly *p, float x) {
    float y = 0;
    for (int i = 0; i < p->n; i++) {
        y += p->coeffs[i] * powf(x, i);
    }
    return y;
}

struct poly *poly_add(struct poly *p1, struct poly *p2) {
    int n = p1->n > p2->n ? p1->n : p2->n;
    struct poly *p = poly_new(n);
    for (int i = 0; i < n; i++) {
        float c1 = i < p1->n ? p1->coeffs[i] : 0;
        float c2 = i < p2->n ? p2->coeffs[i] : 0;
        p->coeffs[i] = c1 + c2;
    }
    return p;
}

struct poly *poly_mul(struct poly *p1, struct poly *p2) {
    int n = p1->n + p2->n - 1;
    struct poly *p = poly_new(n);
    for (int i = 0; i < p1->n; i++) {
        for (int j = 0; j < p2->n; j++) {
            p->coeffs[i + j] += p1->coeffs[i] * p2->coeffs[j];
        }
    }
    return p;
}

struct poly *poly_mul2(struct poly *p1, struct poly *p2) {
    int n = p1->n + p2->n - 1;
    struct poly *p = poly_new(n);
    for (int i = 0; i < p1->n; i++) {
        for (int j = 0; j < p2->n; j++) {
            p->coeffs[i + j] += p1->coeffs[i] * p2->coeffs[j];
        }
    }
    return p;
}

struct poly *poly_read(char *str) {
    int n = 0;
    for (int i = 0; str[i] != '\0'; i++) {
        if (str[i] == 'x') {
            n++;
        }
    }
    struct poly *p = poly_new(n);
    char *token = strtok(str, " ");
    int i = 0;
    while (token != NULL) {
        char *endptr;
        float c = strtof(token, &endptr);
        if (endptr != token) {
            p->coeffs[i++] = c;
        }
        token = strtok(NULL, " ");
    }
    return p;
}


// test poly
int main() {
    struct poly *p1 = poly_new(3, 1, 2, 3);
    struct poly *p2 = poly_new(3, 4, 5, 6);
    struct poly *p3 = poly_add(p1, p2);
    struct poly *p4 = poly_mul(p1, p2);
    poly_print(p1);
    poly_print(p2);
    poly_print(p3);
    poly_print(p4);
    poly_free(p1);
    poly_free(p2);
    poly_free(p3);
    poly_free(p4);
    return 0;
}





