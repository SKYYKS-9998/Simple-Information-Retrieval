from search import *

if __name__ == '__main__':
    infoRetrie = InfoRetrie()
    while True:
        print("Type to search: ", end="")
        search_str = input()

        if search_str == 'q':
            print('Exiting...')
            exit(0)

        count = 0
        rating = 0
        result = infoRetrie.do_search(search_str)
        if len(result) == 0:
            print("No result found!\n")
        for i in result:
            print(i)
            count += 1
            print("**********\nDoes this result match your requirement?\nType Y if so, otherwise type N")
            print("**********\nType n to show next result\nType d to start a new search\nType q to exit\n**********")
            usr_input = input()
            rating = rating if usr_input == 'N' else rating + 1
            if usr_input == 'd':
                break
            elif usr_input == 'q':
                rating = rating * 100.0 / count
                print("本次检索准确度评价：", rating)
                print('Exiting...')
                exit(0)
            else:
                continue
        rating = rating * 100.0 / count
        print("本次检索准确度评价：", rating)
