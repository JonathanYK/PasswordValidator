import sys
import random
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from collections import namedtuple
from logger import logger


class PasswordValidator:
    def __init__(self):
        """
        initiating PasswordValidator instance
        """
        logger.printmessage("-*-*-*Password Validator Started (by Yonatan Kalma)*-*-*-\n")
        self.driver = None
        self.SelectedCriterias = []

    @staticmethod
    def createWebDriver():
        """
        Update chromedriver path here, in future this path will be retrieved from encrypted DB
        :return:
        """
        return webdriver.Chrome(executable_path="C:\Projects\pyCharm\ChromeWebdriver\chromedriver.exe")

    def initValidator(self):
        """
        Initiating the Password Validator and connecting to https://passwordsgenerator.net/
        :return:
        """

        try:
            self.driver = self.createWebDriver()

            self.driver.get("https://passwordsgenerator.net/")
            logger.printmessage("Connected successfully to https://passwordsgenerator.net//")

        except TimeoutException as e:
            logger.printmessage(e + "Timeout exception occurred!\n" + e)

        except:
            e = sys.exc_info()[0]
            logger.printmessage("Exception occurred! Please review the log:\n" + e)

    def assignPasswordRandomLength(self):
        """
        Assigning random length of all available lengths
        :return:
        """
        availablePasswordLengths = self.driver.find_element_by_id("pgLength").find_elements_by_tag_name("option")
        self.selectedLength = random.choice(availablePasswordLengths)
        logger.printmessage("Selected Password Length is: "f"{self.selectedLength.text}")
        self.selectedLength.click()

    def getGeneratedPassword(self, criteriaAmount=None):
        """
        Extracting the last transaction 'Latest Transactions' on main explorer in 'https://www.blockchain.com/'
        :return:
        """
        passwordCriterias = self.driver.find_elements_by_xpath("/html/body/div/div[2]")[0].\
            find_elements_by_class_name("chboxr")
        passwordCriteriaNames = self.driver.find_elements_by_class_name("chboxl")

        # Removing first element (Password Length selection):
        passwordCriterias.pop(0)
        passwordCriteriaNames.pop(0)

        # Removing already selected criterias:
        for Criteria in passwordCriterias:
            if Criteria.find_element_by_tag_name("input").is_selected():
                Criteria.find_element_by_tag_name("input").click()

        # Remove the irrelevant last criterias (consider dynamic amount from user - defined as temp):
        temp = 3
        del passwordCriterias[-temp:]
        del passwordCriteriaNames[-(temp + 2):]

        # Namedtouple that holds the criteria object, it's text and it's validation function name:
        criteriaTuple = namedtuple('criteriaTuple', ['criteriaObj', 'criteriaText', 'criteriaValidationFunc'])
        criteriaArr = []
        for i, criteria in enumerate(passwordCriterias):
            # Clearing validationFuncName - Removing spaces and ':'
            fixedValFunc = self.fixValidationFuncName(dirtyName=passwordCriteriaNames[i].text)

            criteriaArr.append(criteriaTuple(criteria, criteria.text, fixedValFunc))
        # Validation there is more password criterias then the criterias amount defined by the user,
        # then selecting criteriaAmount criterias:
        if criteriaAmount <= len(passwordCriterias):
            for criteria in range(criteriaAmount):
                selected = random.choice(criteriaArr)
                self.SelectedCriterias.append(selected)
                criteriaArr.remove(selected)

        else:
            logger.printmessage("Criterias amount is higher then available criterias amount!\n "
                                "Please decrease criterias amount!")
            return False

        # Selecting the checkboxes of the selected criterias:
        for Criteria in self.SelectedCriterias:
            Criteria.criteriaObj.find_element_by_tag_name("input").click()

        # generating the password according the selected criterias:
        self.driver.find_elements_by_xpath("/html/body/div/div[3]/div[1]")[0].click()
        time.sleep(2)
        generatedPassword = self.driver.find_elements_by_xpath("/html/body/div/div[4]/div[2]/input")[0].get_attribute(
            "value")
        logger.printmessage("Generated Password: "f"{generatedPassword}")
        return generatedPassword

    @staticmethod
    def fixValidationFuncName(dirtyName=None):
        clearName = dirtyName.replace(' ', '').replace(':', '')
        return clearName

    def validateGeneratedPassword(self, generatedPassword=None):
        # Validate Password Length:
        if int(self.selectedLength.text) != len(generatedPassword):
            logger.printmessage("Generated Password Length Wrong!")

        validationSuccess = True
        for validateCriteria in self.SelectedCriterias:
            retval = globals()[validateCriteria.criteriaValidationFunc](generatedPassword)

            if not retval:
                logger.printmessage(f"The password '{generatedPassword}' generated wrong!")
                logger.printmessage(f"Failed on {validateCriteria.criteriaValidationFunc} validation function!")
                validationSuccess &= False

        if validationSuccess:
            logger.printmessage(f"The password '{generatedPassword}' Validated successfully with all it's criterias!")

    def closeDriver(self):
        logger.printmessage("Password Validator Finished! Closing...")
        time.sleep(2)
        if self.driver:
            self.driver.quit()


# There is another approach for the below logic:
# There is an option to create a dictionary of validationFunc and desired chars:
# it will require only one validation function that will receive the desired chars.

def IncludeSymbols(generatedPassword=None):
    retval = True
    chars = set('+[},!{^=:|#%-);<>~`_(-$^%')
    if not any((c in chars) for c in generatedPassword):
        retval = False
    return retval


def IncludeNumbers(generatedPassword=None):
    retval = True
    chars = set('0123456789')
    if not any((c in chars) for c in generatedPassword):
        retval = False
    return retval


def IncludeLowercaseCharacters(generatedPassword=None):
    retval = True
    chars = set('abcdefghijklmnopqrstuvwxyz')
    if not any((c in chars) for c in generatedPassword):
        retval = False
    return retval


def IncludeUppercaseCharacters(generatedPassword=None):
    retval = True
    chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    if not any((c in chars) for c in generatedPassword):
        retval = False
    return retval


def ExcludeSimilarCharacters(generatedPassword=None):
    retval = True
    chars = set('il1o0O')
    if any((c in chars) for c in generatedPassword):
        retval = False
    return retval


def ExcludeAmbiguousCharacters(generatedPassword=None):
    retval = True
    chars = set('{}[]()/"`~\,;:.<>')
    if any((c in chars) for c in generatedPassword):
        retval = False
    return retval
