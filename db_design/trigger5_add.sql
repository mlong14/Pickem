--description: 14. Any new bid for a particular item must have a higher amount than any of the previous bids for that particular item.

PRAGMA foreign_keys = ON;
drop trigger if exists high_bid_trig;
create trigger high_bid_trig
before insert on Bid
for each row
when exists (
	select 1
	from Bid b
	where b.ItemID = new.ItemID
	and b.Amount >= new.Amount
	union
	select 1
	from Item i
	where i.ItemID = new.ItemID
	and i.Currently > new.Amount
)
begin
  select raise(rollback,"Bid must be higher than all previous bids");
end;