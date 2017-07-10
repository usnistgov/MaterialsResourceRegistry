<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    version="1.0">
    <xsl:output method="text" omit-xml-declaration="yes" indent="no"/>

    <xsl:template match="/">
        <xsl:for-each select="//profile/table">
            <xsl:apply-templates select="."/>
            <!--Write 2 tabs and a new line-->
            <xsl:text>&#x9;&#x9;&#xa;</xsl:text>
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="//profile/table">
        <!-- TABLE VALUES -->
        <!--Write Headers-->
        <xsl:for-each select="descendant::headers/column">
            <!--Write Header-->
            <xsl:value-of select="."/>
            <!--Write separator-->
            <xsl:if test="position() != last()">
				<xsl:text>,</xsl:text>
			</xsl:if>
        </xsl:for-each>
        <xsl:text>&#xa;</xsl:text>
        <xsl:for-each select="descendant::rows/row">
            <xsl:for-each select="column">
                <!--Write value-->
                <xsl:value-of select="."/>
                <!--Write separator-->
                <xsl:if test="position() != last()">
				<xsl:text>,</xsl:text>
			</xsl:if>
            </xsl:for-each>
            <xsl:text>&#xa;</xsl:text>
        </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>

