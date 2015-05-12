drop table if exists entries;
create table entries (
    short_url integer primary key autoincrement,
    long_url text not null unique
);
