load_query = """
            select
            fw.id,
            fw.title,
            fw.description,
            fw.rating as imdb_rating,
            array_agg(distinct g.name) as genre,
            array_agg(distinct p.full_name) filter (WHERE pfw.role = 'director') as director,
            array_agg(distinct p.full_name) filter (where pfw.role = 'actor') as actors_names,
            array_agg(distinct p.full_name) filter (where pfw.role = 'writer') as writers_names,
            array_agg(distinct jsonb_build_object('id', p.id, 'name', p.full_name)) filter (where pfw.role = 'actor') as actors,
            array_agg(distinct jsonb_build_object('id', p.id, 'name', p.full_name)) filter (where pfw.role = 'writer') as writers
            from content.film_work fw
            left join content.person_film_work as pfw on pfw.film_work_id = fw.id
            left join content.person as p on p.id = pfw.person_id
            left join content.genre_film_work gfw on gfw.film_work_id = fw.id
            left join content.genre g on g.id = gfw.genre_id
            where greatest(fw.modified,  p.modified, g.modified) > '%s'
            group by fw.id
            order by greatest(fw.modified,  max(p.modified), max(g.modified)) asc;
"""