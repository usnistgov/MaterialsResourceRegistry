<xsl:stylesheet version="1.0" xmlns:pyth="uri:params" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="text" omit-xml-declaration="yes" indent="no"/>


	<xsl:param name="Date" />
	<xsl:variable name="xml" select="pyth:params()" />
	<!--<xsl:template match="/">-->
	<!--<name_is>-->
		<!--<xsl:for-each select="$params">-->
			<!--<xsl:value-of select="." />-->
		<!--</xsl:for-each>-->
	<!--</name_is>-->
	<!--</xsl:template>-->

	<xsl:template match="/">

		<xsl:text>$$  POP File
$$ CREATED </xsl:text><xsl:value-of select="$Date" />
<xsl:text>
$$
$$</xsl:text>
		<xsl:text>&#xa;</xsl:text><!--new line-->
        <xsl:for-each select="$xml">
            <xsl:apply-templates select="."/>
            <xsl:text>&#xa;&#xa;</xsl:text>
        </xsl:for-each>
    </xsl:template>

	<xsl:template match="experiment">

		<xsl:number count="//profile/table/rows/row"/>
		<xsl:text>TABLE</xsl:text>
		<xsl:text>&#xa;</xsl:text>
		<xsl:text>CREATE_NEW_EQ @@,0</xsl:text>
		<xsl:text>&#xa;</xsl:text>

		<!-- CHANGE_ST COMP -->
		<xsl:text>CHANGE_ST COMP </xsl:text>
		<xsl:for-each select="descendant::constituents/constituent">
			<xsl:value-of select="element"/>
			<xsl:if test="position() != last()">
				<xsl:text>, </xsl:text>
			</xsl:if>
		</xsl:for-each>
		<xsl:text> ENT</xsl:text>
		<xsl:text>&#xa;</xsl:text>

		<!-- CHANGE_STATUS -->
		<xsl:text>CHANGE_STATUS PHASE </xsl:text>
		<xsl:value-of select="descendant::material/phase/name"/>
		<xsl:text> =ENT 1</xsl:text>
		<xsl:text>&#xa;</xsl:text>

		<!-- S-COND -->
		<xsl:text>S-COND  N=1 P=101325</xsl:text>
		<xsl:text>&#xa;</xsl:text>

		<!-- S-COND -->
		<xsl:text>S-COND  </xsl:text>
		<xsl:for-each select="descendant::constituents/constituent">
			<!-- mole or mass ? -->
			<xsl:choose>
				<xsl:when test="contains(ancestor::material/Composition/quantityUnit, 'mass') ">
					<xsl:text>w(</xsl:text>
					<xsl:value-of select="element"/>
					<xsl:text>)=</xsl:text>
					<xsl:value-of select="quantity"/>
				</xsl:when>
				<xsl:when test="contains(ancestor::material/Composition/quantityUnit, 'mole') ">
					<xsl:text>X(</xsl:text>
					<xsl:value-of select="element"/>
					<xsl:text>)=</xsl:text>
					<xsl:value-of select="1 - purity"/>
				</xsl:when>
			</xsl:choose>

			<!-- percent of fraction ? -->
			<!-- TODO: if mass/mole percent selected in the form, a percentage should be found in the XML
				so no need to divide by 100 during transformation ?-->
			<!--
				<xsl:choose>
					<xsl:when test="contains(//material/Composition/quantityUnit, 'percent') ">
						<xsl:value-of select="quantity div 100"/>
					</xsl:when>
					<xsl:when test="contains(//material/Composition/quantityUnit, 'fraction') ">
						<xsl:value-of select="quantity"/>
					</xsl:when>
				</xsl:choose>
				-->
			<!-- Print a comma if not last one of the list -->
			<xsl:if test="position() != last()">
				<xsl:text>, </xsl:text>
			</xsl:if>
		</xsl:for-each>
		<xsl:text>&#xa;</xsl:text>

		<!-- S-COND Temperature-->
		<xsl:text>S-COND  T=@</xsl:text>
		<xsl:text>&#xa;</xsl:text>

		<!-- EXPERIMENT -->
		<xsl:text>EXPERIMENT DT (</xsl:text>
		<xsl:value-of select="descendant::material/phase/name"/>
		<xsl:text>,</xsl:text>
		<xsl:value-of select="descendant::diffusingSpecies/element"/>
		<xsl:text>)=</xsl:text>
		<xsl:text>&#xa;</xsl:text>

		<!-- TABLE VALUES -->
		<xsl:text>TABLE VALUES</xsl:text>
		<xsl:text>&#xa;</xsl:text>
		<!--Write Headers-->
		<xsl:for-each select="descendant::profile/table/headers/column">
			<!--Write Header-->
			<xsl:value-of select="."/>
			<!--Write 2 tabs-->
			<xsl:text>&#x9;&#x9;</xsl:text>
		</xsl:for-each>
		<xsl:text>&#xa;</xsl:text>
		<xsl:for-each select="descendant::profile/table/rows/row">
			<xsl:for-each select="column">
				<!--Write value-->
				<xsl:value-of select="."/>
				<!--Write 2 tabs-->
				<xsl:text>&#x9;&#x9;</xsl:text>
			</xsl:for-each>
			<xsl:text>&#xa;</xsl:text>
		</xsl:for-each>
		<xsl:text>TABLE END</xsl:text>
		<!--<xsl:value-of select="$file"/>-->
	</xsl:template>


</xsl:stylesheet>