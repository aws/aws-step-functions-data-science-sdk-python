This section describes the recommended process of verifying the validity of the
AWS Data Science Workflows Python SDK's compiled distributions on
`PyPI <https://pypi.org/project/stepfunctions/>`__.

Whenever you download an application from the internet, we recommend that you
authenticate the identity of the software publisher and check that the
application is not altered or corrupted since it was published. This protects
you from installing a version of the application that contains a virus or other
malicious code.

If after running the steps in this topic, you determine that the distribution
for the AWS Data Science Workflows Python SDK is altered or corrupted, do NOT
install the package. Instead, contact AWS Support (https://aws.amazon.com/contact-us/).

AWS Data Science Workflows Python SDK distributions on PyPI are signed using
GnuPG, an open source implementation of the Pretty Good Privacy (OpenPGP)
standard for secure digital signatures. GnuPG (also known as GPG) provides
authentication and integrity checking through a digital signature. For more
information about PGP and GnuPG (GPG), see http://www.gnupg.org.

The first step is to establish trust with the software publisher. Download the
public key of the software publisher, check that the owner of the public key is
who they claim to be, and then add the public key to your keyring. Your keyring
is a collection of known public keys. After you establish the authenticity of
the public key, you can use it to verify the signature of the application.

Topics
~~~~~~

1. `Installing the GPG Tools <#installing-the-gpg-tools>`__
2. `Authenticating and Importing the Public Key <#authenticating-and-importing-the-public-key>`__
3. `Verify the Signature of the Package <#verify-the-signature-of-the-package>`__

Installing the GPG Tools
~~~~~~~~~~~~~~~~~~~~~~~~

If your operating system is Linux or Unix, the GPG tools are likely already
installed. To test whether the tools are installed on your system, type
**gpg** at a command prompt. If the GPG tools are installed, you see a GPG
command prompt. If the GPG tools are not installed, you see an error stating
that the command cannot be found. You can install the GnuPG package from a
repository.

**To install GPG tools on Debian-based Linux**

From a terminal, run the following command: **apt-get install gnupg**

**To install GPG tools on Red Hat–based Linux**

From a terminal, run the following command: **yum install gnupg**

Authenticating and Importing the Public Key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The next step in the process is to authenticate the AWS Data Science Workflows
Python SDK public key and add it as a trusted key in your GPG keyring.

To authenticate and import the AWS Data Science Workflows Python SDK public key

1. Copy the key from the following text and paste it into a file called
`data_science_workflows.key`. Make sure to include everything that follows:

.. code-block:: text

  -----BEGIN PGP PUBLIC KEY BLOCK-----

  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
  /vQojRxttMc=
  =ovUh
  -----END PGP PUBLIC KEY BLOCK-----


2. At a command prompt in the directory where you saved
`data_science_workflows.key`, use the following command to import the AWS Data
Science Workflows Python SDK public key into your keyring:

.. code-block:: text

  gpg --import data_science_workflows.key

The command returns results that are similar to the following:

.. code-block:: text

  gpg: key 60EB103AE314A809: public key "Stepfunctions-Python-SDK-Signing <stepfunctions-developer-experience@amazon.com>" imported
  gpg: Total number processed: 1
  gpg:               imported: 1

Make a note of the key value; you need it in the next step. In the preceding
example, the key value is 60EB103AE314A809.

3. Verify the fingerprint by running the following command, replacing key-value
with the value from the preceding step:

.. code-block:: text

  gpg --fingerprint <key-value>

This command returns results similar to the following:

.. code-block:: text

  pub   rsa4096 2019-10-31 [SC] [expires: 2030-10-31] CC16 0577 B7BF 9D3D 6E5D
  51C5 60EB 103A E314 A809 uid           [ unknown]
  Stepfunctions-Python-SDK-Signing
  <stepfunctions-developer-experience@amazon.com> sub   rsa4096 2019-10-31 [E]
  [expires: 2030-10-31]

Additionally, the fingerprint string should be identical to CC16 0577 B7BF
9D3D 6E5D  51C5 60EB 103A E314 A809, as shown in the preceding example.
Compare the key fingerprint that is returned to the one published on this
page. They should match. If they don't match, don't install the AWS Data
Science Workflows Python SDK package, and contact AWS Support.

Verify the Signature of the Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After you install the GPG tools, authenticate and import the AWS Data Science
Workflows Python SDK public key, and verify that the public key is trusted, you
are ready to verify the signature of the package.

To verify the package signature, do the following.

1. Download the detached signature for the package from PyPI

  Go to the downloads section for the Data Science Workflows Python SDK
  https://pypi.org/project/stepfunctions/#files on PyPI, Right-click on the SDK
  distribution link, and choose "Copy Link Location/Address".

  Append the string ".asc" to the end of the link you copied, and paste this
  new link on your browser.

  Your browser will prompt you to download a file, which is the detatched
  signature associated with the respective distribution. Save the file on your
  local machine.

2. Verify the signature by running the following command at a command prompt
in the directory where you saved signature file and the AWS Data Science
Workflows Python SDK installation file. Both files must be present.

.. code-block:: text

  gpg --verify <path-to-detached-signature-file>

The output should look something like the following:

.. code-block:: text

  gpg: Signature made Thu 31 Oct 12:14:53 2019 PDT
  gpg:                using RSA key CC160577B7BF9D3D6E5D51C560EB103AE314A809
  gpg: Good signature from "Stepfunctions-Python-SDK-Signing <stepfunctions-developer-experience@amazon.com>" [unknown]
  gpg: WARNING: This key is not certified with a trusted signature!
  gpg:          There is no indication that the signature belongs to the owner.
  Primary key fingerprint: CC16 0577 B7BF 9D3D 6E5D  51C5 60EB 103A E314 A809

If the output contains the phrase Good signature from "AWS Data Science
Workflows Python SDK <stepfunctions-developer-experience@amazon.com>", it means
that the signature has successfully been verified, and you can proceed to run
the AWS Data Science Workflows Python SDK package.

If the output includes the phrase BAD signature, check whether you performed the
procedure correctly. If you continue to get this response, don't run the
installation file that you downloaded previously, and contact AWS Support.

The following are details about the warnings you might see:

.. code-block:: text

  WARNING: This key is not certified with a trusted signature! There is no
  indication that the signature belongs to the owner. This refers to your
  personal level of trust in your belief that you possess an authentic public
  key for AWS Data Science Workflows Python SDK. In an ideal world, you would
  visit an AWS office and receive the key in person. However, more often you
  download it from a website. In this case, the website is an AWS website.

  gpg: no ultimately trusted keys found. This means that the specific key is not
  "ultimately trusted" by you (or by other people whom you trust).

For more information, see http://www.gnupg.org.
