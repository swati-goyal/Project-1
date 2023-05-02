# CREATE SEQUENCE IF NOT EXISTS book_id_seq;
# CREATE TABLE "public"."book" (
#     "id" int4 NOT NULL DEFAULT nextval('book_id_seq'::regclass),
#     "title" varchar(80),
#     "isbn" varchar(20),
#     "author" varchar(40),
#     "year" int4
# );

# ALTER TABLE book
# ADD CONSTRAINT unique_isbn UNIQUE (isbn);

# CREATE TABLE "public"."reviews" (
#     "reviewer_id" int4 NOT NULL,
#     "book_isbn" text NOT NULL,
#     "rating" int4,
#     "review_comment" text,
#     "submitted_at" timestamp,
#     CONSTRAINT "reviews_book_isbn_fkey" FOREIGN KEY ("book_isbn") REFERENCES "public"."book"("isbn"),
#     CONSTRAINT "reviews_reviewer_id_fkey" FOREIGN KEY ("reviewer_id") REFERENCES "public"."users"("user_id")
# );

# CREATE SEQUENCE IF NOT EXISTS users_user_id_seq;
# CREATE TABLE "public"."users" (
#     "user_id" int4 NOT NULL DEFAULT nextval('users_user_id_seq'::regclass),
#     "username" varchar(100) NOT NULL,
#     "password" varchar(20) NOT NULL CHECK (length((password)::text) > 5),
#     "email" varchar(100),
#     PRIMARY KEY ("user_id")
# );
