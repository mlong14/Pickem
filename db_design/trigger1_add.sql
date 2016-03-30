--description: 8. The Current Price of an item must always match the Amount of the most recent bid for that item.

PRAGMA foreign_keys = ON;
drop trigger if exists curr_price_trig;
create trigger curr_price_trig
after insert on Bid
for each row
begin
  update Item set Currently = new.Amount
  where ItemID = new.ItemID;
end;
