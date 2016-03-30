--description: 9. A user may not bid on an item he or she is also selling.

PRAGMA foreign_keys = ON;
drop trigger if exists own_bid_trig;
create trigger own_bid_trig
before insert on Bid
for each row
when exists (
	select *
	from Item i
	where i.ItemID = new.ItemID
	and i.Seller = new.UserID
)
begin
  select raise(rollback,"A user cannot bid on their own item");
end;