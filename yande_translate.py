from mysql_tool import MySqlTool


def translate():
    mysql = MySqlTool()

    tag_dict = {}
    tag_data = mysql.query('SELECT en, cn FROM yande_tag')
    for tag in tag_data:
        tag_dict[tag[0]] = tag[1]

    update_data = mysql.query('SELECT id, en_tag FROM yande_img WHERE cn_tag IS NULL')
    if not update_data:
        return
    for data in update_data:
        data_id = data[0]
        en_tag = data[1]
        if not en_tag:
            continue
        en_tag_list = en_tag.split(',')
        if not en_tag_list:
            continue
        cn_tag_list = []
        for en in en_tag_list:
            if en in tag_dict:
                cn_tag_list.append(tag_dict[en])
            else:
                cn_tag_list.append('*')
        cn_tag = '|'.join(cn_tag_list)
        mysql.execute('UPDATE yande_img SET cn_tag = %s WHERE id = %s', (cn_tag, data_id))


if __name__ == '__main__':
    translate()
