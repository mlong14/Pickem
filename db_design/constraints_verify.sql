
-- 2
select 1
from Item i
where not exists (
	select *
	from User u
	where u.UserID = i.Seller
)
union
select 1
from Bid b
where not exists (
	select *
	from User u
	where u.UserID = b.UserID
);

--4
select *
from Bid b
where not exists (
	select *
	from Item i
	where i.ItemID = b.ItemID
);

--5
select *
from Category c
where not exists (
	select *
	from Item i
	where i.ItemID = c.ItemID
);