#include <ngx_config.h>
#include <ngx_core.h>
#include <nginx.h>

#include <stdio.h>

int main(int argc, char *argv[]) {
    ngx_debug_init();

    ngx_time_init();

    if (argc == 0) {
        printf("should provide prefix directory.\n");
        return 1;
    }

    ngx_log_t *log;
    u_char *ngx_prefix = (u_char *)argv[1];
    u_char *ngx_error_log = (u_char *)"logs/error.log";

    log = ngx_log_init(ngx_prefix, ngx_error_log);
    if (log == NULL) {
        return 1;
    }

    ngx_log_error(NGX_LOG_ALERT, log, ngx_errno,
                          ngx_close_file_n " built-in log failed");

    ngx_str_t str;
    ngx_str_set(&str, "Hello, world!");
    printf("str: %s\n", str.data);

    ngx_int_t num = 42;
    printf("num: %ld\n", num);

    ngx_pool_t *pool = ngx_create_pool(1024, log);
    if (pool == NULL) {
        printf("Failed to create memory pool\n");
        return 1;
    }

    ngx_chain_t *chain = ngx_pcalloc(pool, sizeof(ngx_chain_t));
    if (chain == NULL) {
        printf("Failed to allocate memory for chain\n");
        return 1;
    }
    chain->buf = ngx_calloc_buf(pool);
    if (chain->buf == NULL) {
        printf("Failed to allocate memory for buf\n");
        return 1;
    }

    ngx_buf_t *buf = chain->buf;
    buf->pos = str.data;
    buf->last = str.data + str.len;
    buf->memory = 1;

    printf("chain: %p, chain->buf: %p, chain->buf->pos: %s\n", chain, buf, buf->pos);

    ngx_destroy_pool(pool);
    return 0;

    // TODO: try 'ngx_array_t config_dump;' and 'ngx_rbtree_t config_dump_rbtree;'
}
