from class_db_handler import DatabaseHandler


def main():
    dbhandler = DatabaseHandler()

    #number = 4
    #for number in range(1, 10):
    #    dbhandler.save_to_database( title = f"title {number}", source = f"test source {number}", url = f"testurl {number}", article_content = f"testarticle {number}", catagory="Crypto")
   
    dbhandler.remove_old_articles(0)
    dbhandler.remove_old_articles(1)
    dbhandler.remove_old_articles(2)
    #dbhandler.get_last_article_id()
    return None

if __name__ == "__main__":
    main()