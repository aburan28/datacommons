\set agg_top_n 10

select date_trunc('second', now()) || '-- Starting EPA aggregate computation...';

select date_trunc('second', now()) || '-- Dropping associations table';
drop table if exists assoc_epa_echo;

select date_trunc('second', now()) || '-- Creating associations table';
create table assoc_epa_echo as
    select distinct entity.entity_id, case.id::integer as case_id, defendant.id as defendant_id
    from epa_echo_case c
    inner join epa_echo_defendant d on d.id = c.defendant_id
    inner join matchbox_entityattribute entity on value::smallint = contractor.contractor_ext_id
    where entity.namespace = 'urn:pogo:contractor'
;

select date_trunc('second', now()) || ' -- create index assoc_epa_echo_entity_id on assoc_epa_echo (entity_id)';
create index assoc_epa_echo_entity_id on assoc_epa_echo (entity_id);
select date_trunc('second', now()) || ' -- create index assoc_epa_echo_misconduct_id on assoc_epa_echo (misconduct_id)';
create index assoc_epa_echo_misconduct_id on assoc_epa_echo (misconduct_id);


-- Totals

select date_trunc('second', now()) || '-- Dropping totals table';
drop table if exists agg_epa_echo_totals;

select date_trunc('second', now()) || '-- Creating totals table';

create table agg_epa_echo_totals as
    with misconduct_by_cycle as (
        select
            entity.id as entity_id,
            date + date % 2 as cycle,
            count(*) as count,
            sum(amount) as amount
        from epa_echo_case
        inner join epa_echo_penalty
        inner join epa_echo_facility
        inner join epa_echo_defendant
        inner join epa_echo_milestone
        inner join assoc_epa_echo assoc on assoc.misconduct_id = misconduct.id
        inner join matchbox_entity entity on assoc.entity_id = entity.id
        group by entity.id, date_year + date_year % 2
    )
    select entity_id, cycle, count, amount
    from misconduct_by_cycle

    union all

    select entity_id, -1 as cycle, sum(count) as count, sum(amount) as amount
    from misconduct_by_cycle
    group by entity_id
;
select date_trunc('second', now()) || ' -- create index agg_epa_echo_totals__entity_id on agg_epa_echo_totals (entity_id)';
create index agg_epa_echo_totals__entity_id on agg_epa_echo_totals (entity_id);


-- Top 10 Instances

select date_trunc('second', now()) || '-- Dropping aggregate table';
drop table if exists agg_epa_echo_contractor_misconduct;

select date_trunc('second', now()) || '-- Creating aggregate table';

create table agg_epa_echo_contractor_misconduct as
    with misconduct_by_cycle as (
        select
            date_year + date_year % 2 as cycle,
            date_year as year,
            date_significance,
            entity.id as contractor_entity,
            contractor.name as contractor,
            contracting_party,
            penalty_amount,
            instance,
            disposition,
            misconduct_type,
            misconduct.url as misconduct_url,
            rank() over (partition by entity.id, date_year + date_year % 2 order by penalty_amount desc, instance) as rank
        from pogo_misconduct misconduct
        inner join pogo_contractor contractor on misconduct.contractor_id = contractor.id
        inner join assoc_epa_echo assoc on assoc.misconduct_id = misconduct.id
        inner join matchbox_entity entity on assoc.entity_id = entity.id
    )
    select cycle, year, date_significance, contractor_entity, contractor, contracting_party, penalty_amount, instance, disposition, misconduct_type, misconduct_url
    from misconduct_by_cycle
    where rank <= :agg_top_n

    union all

    select cycle, year, date_significance, contractor_entity, contractor, contracting_party, penalty_amount, instance, disposition, misconduct_type, misconduct_url
    from (
        select -1 as cycle, year, date_significance, contractor_entity, contractor, contracting_party, penalty_amount, instance, disposition, misconduct_type, misconduct_url,
            rank() over (partition by contractor_entity order by penalty_amount desc) as rank
        from misconduct_by_cycle
    ) x
    where rank <= :agg_top_n
;

select date_trunc('second', now()) || ' -- create index agg_epa_echo_contractor_misconduct__contractor_entity on agg_epa_echo_contractor_misconduct (contractor_entity)';
create index agg_epa_echo_contractor_misconduct__contractor_entity on agg_epa_echo_contractor_misconduct (contractor_entity);

