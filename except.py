if __name__ == "__main__":
    flag = True
    try:
        print("Hello")
        assert False
        print("Middle")
    except AssertionError:
        print('Welcome to Prometheus!!!')