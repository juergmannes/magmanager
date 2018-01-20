drop table if exists mags;
create table mags (
  id integer primary key autoincrement,
  title text not null
);
drop table if exists users;
create table users (
  id integer primary key autoincrement,
  short_name text not null
);
drop table if exists users_mags;
create table users_mags (
  id integer primary key autoincrement,
  users_id integer,
  mags_id integer
);
insert into mags (title) values ('c''t');
insert into mags (title) values ('Spektrum der Wissenschaft');
insert into mags (title) values ('brand 1');
insert into users (short_name) values ('AAA');
insert into users (short_name) values ('BBB');
insert into users (short_name) values ('CCC');
/*insert into users_mags (users_id,mags_id) values (1,1);
insert into users_mags (users_id,mags_id) values (2,1);
insert into users_mags (users_id,mags_id) values (2,2);
insert into users_mags (users_id,mags_id) values (3,2);
insert into users_mags (users_id,mags_id) values (3,3);*/