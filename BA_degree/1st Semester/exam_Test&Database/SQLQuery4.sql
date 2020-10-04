
select first_name, last_name, employee_id, library_employee_id, hourly_wage, weekly_hours, [type] from Person as p
inner join PersonType as pp on p.person_type_id = pp.id

inner join LibraryEmployee as lb on pp.library_employee_id = lb.employee_id

inner join LibraryEmployeeType as lbt on lb.library_employee_type_id = lbt.id



