from bd.bd_operations import BaseData


def main():
    bd = BaseData()
    bd.create_bd_if_not_exists()
    bd.add_in_db('51511515135')
    bd.add_in_db('5123412312')

    users = bd.took_all_data_about_user()
    print(users)
    bd.close_connection_into_bd()

if __name__ == '__main__':
    main()