drop table if exists query;
create table query (
  id integer primary key autoincrement,
  firstname text not null,
  lastname text not null
);

drop table if exists info;
create table info (
  id integer primary key autoincrement,
  nb_names integer not null,
  ageL integer not null,
  ageH integer not null,
  caps text not null
);
