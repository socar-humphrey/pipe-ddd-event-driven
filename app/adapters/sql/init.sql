create table users
(
	id varchar,
	name varchar,
	password varchar,
	created_at datetime default current_date,
	updated_at datetime default current_date
);

create table posts
(
	id varchar,
	title varchar,
	content varchar(200),
	author varchar
		constraint posts_user_id__fk
			references users (id)
				on update cascade on delete cascade,
	created_at datetime default current_date,
	updated_at datetime default current_date
);


