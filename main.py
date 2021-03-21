# Password validation on 'https://www.blockchain.com/' using Selenium Chrome webdriver by Yonatan Kalma
import chromeWebdriverConfig as CWD


def main():
    passValidator = CWD.PasswordValidator()

    # Make sure the chrome webdriver located at C:\Projects\pyCharm\ChromeWebdriver\chromedriver.exe
    passValidator.initValidator()

    passValidator.assignPasswordRandomLength()
    generatedPassword = passValidator.getGeneratedPassword(criteriaAmount=3)

    passValidator.validateGeneratedPassword(generatedPassword=generatedPassword)
    passValidator.closeDriver()


if __name__ == '__main__':
    main()




