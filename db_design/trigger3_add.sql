--description: 11. No auction may have a bid before its start time or after its end time.

PRAGMA foreign_keys = ON;
drop trigger if exists in_time_window_trig;
create trigger in_time_window_trig
before insert on Bid
for each row
when exists (
	select *
	from Item i
	where i.ItemID = new.ItemID
	and (new.Time < i.Started
	or new.Time > i.Ends)
)
begin
  select raise(rollback,"This item is not being auctioned at this time");
end;